import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.env.local')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
PORT = int(os.getenv('PORT', 5050))
SYSTEM_MESSAGE = (
    "You are a helpful and concise WhatsApp assistant.",
    "You are made by RMG, a saudi company focused on digitalization and automation."
)

if not OPENAI_API_KEY:
    raise ValueError('Missing the OPENAI_API_KEY environment variable.')
