import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Print what's loaded (for debugging)
print("Environment variables:")
print(f"TWILIO_ACCOUNT_SID: {os.getenv('TWILIO_ACCOUNT_SID')}")
print(f"TWILIO_AUTH_TOKEN: {os.getenv('TWILIO_AUTH_TOKEN')[:10]}..." if os.getenv('TWILIO_AUTH_TOKEN') else "Not set")
print(f"TWILIO_PHONE_NUMBER: {os.getenv('TWILIO_PHONE_NUMBER')}")

# Test Twilio
try:
    from twilio.rest import Client
    
    client = Client(
        os.getenv('TWILIO_ACCOUNT_SID'),
        os.getenv('TWILIO_AUTH_TOKEN')
    )
    
    # Send test message
    message = client.messages.create(
        body="Test from Library Safety System - if you receive this, SMS is working!",
        from_=os.getenv('TWILIO_PHONE_NUMBER'),
        to="+254113630662"  # Your number
    )
    
    print(f"SUCCESS: Test message sent with SID: {message.sid}")
    
except Exception as e:
    print(f"ERROR: {e}")