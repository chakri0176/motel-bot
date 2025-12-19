Sunset Motel AI Receptionist 🏨
===============================

> **⚠️ BETA VERSION** - This project is currently in beta. Expect frequent updates, improvements, and potential breaking changes as we continue development.

Overview
--------

Sunset Motel AI Receptionist is an intelligent voice-based booking system powered by LangChain and Groq's LLaMA model. The AI agent, "Sarah," handles hotel reservations through natural voice conversations, managing room availability checks and booking confirmations in real-time.

Features
--------

*   🎙️ **Voice-Optimized Responses** - Clean, TTS-friendly output without markdown or special characters
    
*   🤖 **Intelligent Tool Usage** - Automatically checks room availability and processes bookings
    
*   💬 **Natural Conversations** - Conversational AI that speaks like a real receptionist
    
*   🔄 **Real-Time WebSocket Communication** - Instant bidirectional communication
    
*   🗄️ **Supabase Integration** - Persistent storage for rooms and bookings
    
*   📊 **Conversation History Management** - Maintains context throughout the call
    

Tech Stack
----------

*   **FastAPI** - Modern, high-performance web framework
    
*   **LangChain** - Framework for building LLM applications
    
*   **Groq** - Lightning-fast LLM inference (LLaMA 3.3 70B)
    
*   **Supabase** - Backend-as-a-Service for database management
    
*   **WebSockets** - Real-time bidirectional communication
    
*   **Python 3.8+** - Core programming language
    

Project Structure
-----------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   .  ├── server.py          # Main FastAPI application with WebSocket endpoint  ├── tools.py           # LangChain tools for room operations  ├── requirements.txt   # Python dependencies  └── README.md         # Project documentation   `

Installation
------------

### Prerequisites

*   Python 3.8 or higher
    
*   Groq API key
    
*   Supabase account and project
    

### Setup

1.  **Clone the repository**
    

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML   `git clone https://github.com/yourusername/sunset-motel-ai.git     cd sunset-motel-ai`

1.  **Install dependencies**
    

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML   `pip install -r requirements.txt`

1.  **Configure environment variables**Create a .env file in the project root:
    

env

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML   `GROQ_API_KEY=your_groq_api_key_here     SUPABASE_URL=your_supabase_url_here     SUPABASE_SERVICE_KEY=your_supabase_service_key_here`

1.  **Set up Supabase Database**Create two tables in your Supabase project:**Rooms Table:**
    

sql

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML   `CREATE TABLE rooms (       id SERIAL PRIMARY KEY,       room_type VARCHAR(50) NOT NULL,       price_per_night DECIMAL(10,2) NOT NULL,       is_available BOOLEAN DEFAULT TRUE     );`

**Bookings Table:**

sql

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML   `CREATE TABLE bookings (       id SERIAL PRIMARY KEY,       guest_name VARCHAR(255) NOT NULL,       room_id INTEGER REFERENCES rooms(id),       check_in_date DATE NOT NULL,       created_at TIMESTAMP DEFAULT NOW()     );`

1.  **Seed sample data (optional)**
    

sql

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML   `INSERT INTO rooms (room_type, price_per_night, is_available) VALUES     ('Queen', 89.99, TRUE),     ('King', 109.99, TRUE),     ('Suite', 179.99, TRUE);`

Usage
-----

### Starting the Server

bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   uvicorn server:app --reload --host 0.0.0.0 --port 8000  ```  The WebSocket endpoint will be available at:  ```  ws://localhost:8000/llm-websocket/{call_id}   `

### WebSocket Protocol

**Client → Server (User Input):**

json

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   {    "interaction_type": "response_required",    "response_id": 1,    "transcript": [      {        "role": "user",        "content": "I'd like to book a room"      }    ]  }   `

**Server → Client (AI Response):**

json

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   {    "response_type": "response",    "response_id": 1,    "content": "I'd be happy to help you book a room. What type would you prefer: Queen, King, or Suite?",    "content_complete": true,    "end_call": false  }   `

Available Tools
---------------

### 1\. Check Room Availability

Checks if a specific room type is available and returns pricing information.

**Parameters:**

*   room\_type (str): Room type to check (Queen, King, Suite)
    

### 2\. Book Reservation

Creates a new booking and marks the room as unavailable.

**Parameters:**

*   name (str): Guest name
    
*   room\_type (str): Desired room type
    
*   date (str): Check-in date
    

AI Agent Behavior
-----------------

"Sarah" is designed to:

*   Greet callers warmly and professionally
    
*   Ask for booking information step-by-step (Name → Room Type → Date)
    
*   Check room availability before confirming bookings
    
*   Keep responses concise (under 2 sentences)
    
*   Speak naturally without technical jargon
    

Future Updates
--------------

This project is actively being developed. Planned features include:

*   🗓️ **Multi-night stays** - Support for check-out dates and duration
    
*   💳 **Payment integration** - Process payments during booking
    
*   📧 **Email confirmations** - Automatic booking confirmations
    
*   🔐 **Guest authentication** - Secure account management
    
*   📊 **Analytics dashboard** - Booking metrics and insights
    
*   🌐 **Multi-language support** - International guest support
    
*   🔔 **SMS notifications** - Booking reminders and updates
    
*   🏷️ **Dynamic pricing** - Seasonal and demand-based pricing
    
*   🔍 **Advanced search** - Filter by amenities and preferences
    

Contributing
------------

Contributions are welcome! This is a beta project, and we appreciate:

*   Bug reports and fixes
    
*   Feature suggestions
    
*   Documentation improvements
    
*   Code optimizations
    

Please open an issue or submit a pull request.

Known Issues
------------

*   Room availability is simplified (doesn't handle date ranges)
    
*   No conflict checking for overlapping bookings
    
*   Limited error handling for edge cases
    
*   Tool execution happens sequentially (could be optimized)