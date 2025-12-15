import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from tools import check_room_availability, book_reservation
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Setup Groq LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    groq_api_key=os.environ.get("GROQ_API_KEY")
)

# Bind tools to LLM
tools = [check_room_availability, book_reservation]
llm_with_tools = llm.bind_tools(tools)

# System message
SYSTEM_MESSAGE = """You are 'Sarah', the front desk AI for Sunset Motel.
- Your voice output is processed by TTS, so DO NOT use special characters, emojis, or markdown.
- Be concise. Speak like a human receptionist, not a robot. 
- Keep responses under 2 sentences.
- If booking, ask for Name, Room Type, and Date one by one.

You have access to these tools:
1. check_room_availability - Check if a room type is available
2. book_reservation - Book a room for a guest"""

def execute_tools(tool_calls):
    """Execute tool calls and return results"""
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        if tool_name == "check_room_availability":
            result = check_room_availability.invoke(tool_args)
        elif tool_name == "book_reservation":
            result = book_reservation.invoke(tool_args)
        else:
            result = f"Unknown tool: {tool_name}"
        
        results.append(result)
    
    return results

# CHANGE 1: Update the route to accept the call_id
@app.websocket("/llm-websocket/{call_id}")
# CHANGE 2: Add call_id to the function arguments
async def websocket_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    conversation_history = [SystemMessage(content=SYSTEM_MESSAGE)]
    
    try:
        # Send initial greeting
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
                if not data['transcript']:
                    continue
                    
                user_transcript = data['transcript'][-1]['content']
                print(f"User said: {user_transcript}")
                
                try:
                    # Add user message to history
                    conversation_history.append(HumanMessage(content=user_transcript))
                    
                    # Get LLM response
                    response = await llm_with_tools.ainvoke(conversation_history)
                    
                    # Check if tools were called
                    if hasattr(response, 'tool_calls') and response.tool_calls:
                        print(f"Tool calls: {response.tool_calls}")
                        
                        # Execute tools
                        tool_results = execute_tools(response.tool_calls)
                        
                        # Add tool results to history
                        conversation_history.append(response)
                        for result in tool_results:
                            conversation_history.append(HumanMessage(content=f"Tool result: {result}"))
                        
                        # Get final response after tool execution
                        final_response = await llm_with_tools.ainvoke(conversation_history)
                        response_text = final_response.content
                        conversation_history.append(final_response)
                    else:
                        response_text = response.content
                        conversation_history.append(response)
                    
                    # Clean up response text
                    response_text = response_text.strip()
                    
                except Exception as e:
                    print(f"Error: {e}")
                    import traceback
                    traceback.print_exc()
                    response_text = "I'm sorry, I missed that. Could you say it again?"

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
        print(f"Call {call_id} disconnected") # We can now print the call_id!
    except Exception as e:
        print(f"WebSocket error: {e}")