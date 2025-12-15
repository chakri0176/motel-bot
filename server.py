import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from tools import check_room_availability, book_reservation
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

llm = ChatGroq(
    model="openai/gpt-oss-120b", 
    temperature=0.2,
    groq_api_key=os.environ.get("GROQ_API_KEY")
)

tools = [check_room_availability, book_reservation]

# 2. Define the Prompt (The "Sarah" Persona)
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are 'Sarah', the front desk AI for Sunset Motel.
    - Your voice output is processed by TTS, so DO NOT use special characters, emojis, or markdown.
    - Be concise. Speak like a human receptionist, not a robot. 
    - Keep responses under 2 sentences.
    - If booking, ask for Name, Room Type, and Date one by one.
    """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 3. Create the Agent (Using the new 'Tool Calling' method)
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

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