import os
import asyncio
import logging

# Set dummy env vars to pass config assertions
os.environ["OPENAI_API_KEY"] = "sk-dummy"
os.environ["TWILIO_ACCOUNT_SID"] = "ACdummy"
os.environ["TWILIO_AUTH_TOKEN"] = "dummy"
os.environ["TWILIO_PHONE_NUMBER"] = "+1234567890"

# Mock RAG config if not in env
os.environ["RAG_API_BASE_URL"] = "https://40-79-241-100.sslip.io/api/v1"
os.environ["RAG_EMAIL"] = "admin@rmg-sa.com"
os.environ["RAG_PASSWORD"] = "Admin@123456"
os.environ["RAG_SESSION_ID"] = "54e7d7fa-4496-43c0-88f5-9ceea5bf4eb5"

from app.services.rag_client import RagClient

async def test_rag():
    client = RagClient()
    print("Logging in...")
    await client.login()
    print(f"Logged in. Token: {client.token[:10]}...")
    
    query = "how much money is needed to start a business"
    print(f"Querying: {query}")
    answer = await client.query(query)
    print("\n--- FINAL ANSWER ---")
    print(answer)

if __name__ == "__main__":
    asyncio.run(test_rag())
