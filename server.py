import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType
from langchain.schema import SystemMessage
from tools import check_room_availability, book_reservation
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CHANGED: Setup Groq LLM
# Model: llama3-70b-8192 is highly recommended for tool use. 
# llama3-8b is faster but might fail to book rooms correctly.
llm = ChatGroq(
    model="llama3-70b-8192", 
    temperature=0.2,
    groq_api_key=os.environ.get("GROQ_API_KEY")
)

tools = [check_room_availability, book_reservation]

system_prompt = """
You are 'Sarah', the front desk AI for Sunset Motel.
- Your voice output is processed by TTS, so DO NOT use special characters, emojis, or markdown.
- Be concise. Speak like a human receptionist, not a robot. 
- Keep responses under 2 sentences.
- If booking, ask for Name, Room Type, and Date one by one.
"""

# Groq works best with the STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION or OPENAI_FUNCTIONS 
# Note: Groq now supports tool calling, so we can stick with standard agent initialization
agent_executor = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, # Safe bet for Llama 3
    agent_kwargs={"system_message": SystemMessage(content=system_prompt)},
    verbose=True,
    handle_parsing_errors=True # Llama 3 sometimes formats output weirdly, this fixes it
)

@app.websocket("/llm-websocket/{call_id}")
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    
    try:
        # Initial greeting
        first_greeting = {
            "response_type": "response",
            "response_id": 0,
            "content": "Thank you for calling Sunset Motel, this is Sarah. How can I help you?",
            "content_complete": True,
            "end_call": False
        }
        await websocket.send_json(first_greeting)

        async for data in websocket.iter_json():
            if data['interaction_type'] == 'update_only':
                continue
            
            if data['interaction_type'] == 'response_required':
                user_transcript = data['transcript'][-1]['content']
                print(f"User said: {user_transcript}")
                
                # Run Groq Agent
                try:
                    ai_response = await agent_executor.ainvoke({"input": user_transcript})
                    response_text = ai_response["output"]
                except Exception as e:
                    print(f"Error: {e}")
                    response_text = "I'm sorry, could you say that again?"

                # Send Response
                response_payload = {
                    "response_type": "response",
                    "response_id": data['response_id'],
                    "content": response_text,
                    "content_complete": True,
                    "end_call": False
                }
                await websocket.send_json(response_payload)
                
    except WebSocketDisconnect:
        print(f"Call {call_id} ended.")