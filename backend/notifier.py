import os
from dotenv import load_dotenv
import time

class Notifier:
    def __init__(self):
        load_dotenv()
        print("🚨 Notifier initialized - Console Mode")
        
    def send_notification(self, to_phone, message):
        """Send notification via console with visual alerts."""
        
        print(f"📞 send_notification called with phone: {to_phone}")
        print(f"📝 send_notification called with message: {message}")
        
        timestamp = time.strftime("%H:%M:%S")
        
        # Console alert with emojis for visibility
        print("\n" + "🚨" * 30)
        print(f"⏰ TIME: {timestamp}")
        print(f"📞 PHONE: {to_phone}")
        print(f"🔔 ALERT: {message}")
        print("🚨" * 30 + "\n")
        
        return True, f"console_alert_{timestamp}"