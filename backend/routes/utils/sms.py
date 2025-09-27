# utils/sms.py
import os
from twilio.rest import Client

# Load from environment
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID") # make environment variables
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN") # make environment variables
FROM_NUMBER = os.getenv("TWILIO_PHONE_NUMBER") # make encironment variables

client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_sms(to_number: str, message: str):
    """Send SMS via Twilio"""
    if not all([ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER]):
        raise RuntimeError("Twilio credentials not set in environment")

    msg = client.messages.create(
        body=message,
        from_=FROM_NUMBER,
        to=to_number
    )
    return msg.sid
