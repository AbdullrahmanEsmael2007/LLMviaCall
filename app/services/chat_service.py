import openai
import httpx
import json
import base64
import io
import asyncio
from app.config import OPENAI_API_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from typing import Optional, Tuple
from app.services.rag_client import RagClient

# Initialize Clients
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
rag_client = RagClient()

async def download_media(media_url: str) -> bytes:
    """Download media from Twilio URL (requires Basic Auth)."""
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
             media_url, 
             auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
             follow_redirects=True
        )
        return response.content

async def analyze_image(media_url: str, media_type: str) -> str:
    """Use GPT-4o Vision to describe the image."""
    try:
        print(f"Analyzing Image: {media_url}")
        image_data = await download_media(media_url)
        base64_image = base64.b64encode(image_data).decode('utf-8')
        data_url = f"data:{media_type};base64,{base64_image}"
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail. If it contains text, transribe it."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Image analysis failed: {e}")
        return "[Error analyzing image]"

async def get_chat_response(
    message_body: str, 
    sender_number: str, 
    media_url: Optional[str] = None, 
    media_type: Optional[str] = None
) -> Tuple[str, Optional[str]]:
    """
    Process user message.
    Flow: Input -> [Whisper/Vision] -> Text -> RAG API -> Output
    Returns: (text_response, optional_media_url)
    """
    
    final_query_parts = []
    
    # 1. Text Input
    if message_body:
        final_query_parts.append(message_body)
    
    # 2. Audio Input (Whisper)
    if media_type and media_type.startswith('audio/'):
        print(f"Processing Audio: {media_type}")
        try:
            audio_bytes = await download_media(media_url)
            ext = media_type.split('/')[-1].replace('x-', '') 
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = f"voice_note.{ext}" 
            
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            transcribed_text = transcription.text
            print(f"Transcribed: {transcribed_text}")
            final_query_parts.append(transcribed_text)
            
        except Exception as e:
            print(f"Audio error: {e}")
            return "I couldn't hear that voice note.", None

    # 3. Image Input (GPT-4o Vision)
    if media_type and media_type.startswith('image/') and media_url:
        image_description = await analyze_image(media_url, media_type)
        print(f"Image Description: {image_description}")
        final_query_parts.append(f"[Image Context: {image_description}]")

    # Combine all inputs
    if not final_query_parts:
        return "Please send text, audio, or an image.", None
        
    full_query = "\n".join(final_query_parts)
    print(f"Final RAG Query: {full_query}")

    # 4. Direct RAG Query
    try:
        rag_answer = await rag_client.query(full_query)
        # Ensure result is string
        return str(rag_answer), None
    except Exception as e:
        print(f"RAG Error: {e}")
        return "Sorry, I am having trouble accessing the system right now.", None
