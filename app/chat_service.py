import openai
from app.config import OPENAI_API_KEY, SYSTEM_MESSAGE
from collections import defaultdict
import asyncio

# Initialize OpenAI Client
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

# In-memory store for conversation history
# Key: Sender's Phone Number, Value: List of messages
# This is non-persistent (cleared on restart)
conversation_history = defaultdict(list)

async def get_chat_response(message_body: str, sender_number: str) -> str:
    """
    Process a user message, update history, and get a response from OpenAI.
    """
    
    # Initialize history if empty
    if not conversation_history[sender_number]:
        conversation_history[sender_number].append({
            "role": "system", 
            "content": SYSTEM_MESSAGE
        })
    
    # Append user message
    conversation_history[sender_number].append({
        "role": "user",
        "content": message_body
    })
    
    try:
        # Call OpenAI Chat Completion
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=conversation_history[sender_number],
            temperature=0.7,
            max_tokens=300
        )
        
        assistant_message = response.choices[0].message.content
        
        # Append assistant response
        conversation_history[sender_number].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message

    except Exception as e:
        print(f"Error calling OpenAI: {e}")
        return "I'm sorry, I encountered an error processing your request."
