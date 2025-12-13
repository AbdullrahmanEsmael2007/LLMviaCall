from fastapi import APIRouter, Request, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
from app.chat_service import get_chat_response

router = APIRouter()

@router.get("/")
async def index_page():
    return "<h1>WhatsApp Bot Server is Running</h1>"

@router.post("/whatsapp")
async def whatsapp_reply(Body: str = Form(...), From: str = Form(...)):
    """
    Handle incoming WhatsApp messages.
    Twilio sends form-encoded data.
    """
    # Get response from the Chat Service
    reply_text = await get_chat_response(Body, From)
    
    # Create TwiML Response
    response = MessagingResponse()
    response.message(reply_text)
    
    return Response(content=str(response), media_type="application/xml")
