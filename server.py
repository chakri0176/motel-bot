import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.tools import render_text_description
from tools import check_room_availability, book_reservation
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# 1. Setup Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",  # Updated to a valid model
    temperature=0.2,
    groq_api_key=os.environ.get("GROQ_API_KEY")
)

tools = [check_room_availability, book_reservation]

# 2. Define the Prompt (ReAct format)
prompt = PromptTemplate.from_template("""
You are 'Sarah', the front desk AI for Sunset Motel.
- Your voice output is processed by TTS, so DO NOT use special characters, emojis, or markdown.
- Be concise. Speak like a human receptionist, not a robot. 
- Keep responses under 2 sentences.
- If booking, ask for Name, Room Type, and Date one by one.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
""")

# 3. Create the Agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

@app.websocket("/llm-websocket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Send initial greeting to Retell
        first_greeting = {
            "response_type": "response",
            "response_id": 0,
            "content": "Thank you for calling Sunset Motel, this is Sarah. How can I help you?",
            "content_complete": True,
            "end_call": False
        }
        await websocket.send_json(first_greeting)

        async for data in websocket.iter_json():
            # Retell sends "interaction_response" events when user speaks
            if data['interaction_type'] == 'update_only':
                continue
            
            if data['interaction_type'] == 'response_required':
                # Check if transcript exists to avoid index errors
                if not data['transcript']:
                    continue
                    
                user_transcript = data['transcript'][-1]['content']
                print(f"User said: {user_transcript}")
                
                # Run the Agent
                try:
                    ai_response = await agent_executor.ainvoke({"input": user_transcript})
                    response_text = ai_response["output"]
                except Exception as e:
                    print(f"Error: {e}")
                    response_text = "I'm sorry, I missed that. Could you say it again?"

                # Send Response to Retell
                response_payload = {
                    "response_type": "response",
                    "response_id": data['response_id'],
                    "content": response_text,
                    "content_complete": True,
                    "end_call": False
                }
                await websocket.send_json(response_payload)
                
    except WebSocketDisconnect:
        print("Client disconnected")