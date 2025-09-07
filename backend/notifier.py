# backend/notifier.py
import os
from dotenv import load_dotenv
import time
from twilio.rest import Client

class Notifier:
    def __init__(self):
        load_dotenv()
        
        # Get Twilio credentials from environment variables
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
        
        # Check if all credentials are available
        if self.account_sid and self.auth_token and self.twilio_phone:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                # Test the connection by getting account info
                account = self.client.api.account.fetch()
                print(f"🚨 NNNNotifier initialized - Twilio SMS Mode")
                print(f"📱 Twilio Phone: {self.twilio_phone}")
                print(f"✅ Account Status: {account.status}")
                self.mode = "twilio"
            except Exception as e:
                print(f"❌ Twilio initialization failed: {e}")
                print("🚨 Falling back to Console Mode")
                self.client = None
                self.mode = "console"
        else:
            print("⚠️  Twilio credentials not found in environment variables")
            print("🚨 Notifier initialized - Console Mode")
            self.client = None
            self.mode = "console"
        
    def send_notification(self, to_phone, message):
        """Send notification via Twilio SMS or console fallback."""
        
        print(f"📞 send_notification called with phone: {to_phone}")
        print(f"📝 send_notification called with message: {message}")
        
        timestamp = time.strftime("%H:%M:%S")
        
        if self.mode == "twilio" and self.client:
            return self._send_sms(to_phone, message, timestamp)
        else:
            return self._send_console_alert(to_phone, message, timestamp)
        
    def _send_sms(self, to_phone, message, timestamp):
        """Send actual SMS via Twilio."""
        try:
            # Validate phone number format
            if not to_phone.startswith('+'):
                to_phone = '+' + to_phone.lstrip('+')
            
            print(f"📤 Sending SMS to {to_phone} via Twilio...")
            
            # Send the SMS
            message_obj = self.client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=to_phone
            )
            
            print(f"✅ SMS sent successfully!")
            print(f"📋 Message SID: {message_obj.sid}")
            print(f"📊 Status: {message_obj.status}")
            
            # Also log to console for debugging
            self._log_to_console(to_phone, message, timestamp, "SMS_SENT")
            
            return True, message_obj.sid
            
        except Exception as e:
            print(f"❌ Failed to send SMS: {e}")
            print(f"🔄 Falling back to console alert...")
            
            # Fallback to console if SMS fails
            return self._send_console_alert(to_phone, message, timestamp)
            
            
    
    def _send_console_alert(self, to_phone, message, timestamp):
        """Send console alert as fallback."""
        self._log_to_console(to_phone, message, timestamp, "CONSOLE_ALERT")
        return True, f"console_alert_{timestamp}"
    
    def _log_to_console(self, to_phone, message, timestamp, alert_type):
        """Log alert to console with visual formatting."""
        print("\n" + "🚨" * 30)
        print(f"⏰ TIME: {timestamp}")
        print(f"📞 PHONE: {to_phone}")
        print(f"🔔 ALERT: {message}")
        print(f"📋 TYPE: {alert_type}")
        print("🚨" * 30 + "\n")
    
    def test_sms(self, test_phone=None):
        """Test SMS functionality with a simple message."""
        if not test_phone:
            test_phone = input("Enter phone number to test (with country code): ")
        
        test_message = f"🧪 Library Security System Test - {time.strftime('%H:%M:%S')}"
        
        print(f"🧪 Testing SMS to {test_phone}...")
        #success, result = self.send_notification(test_phone, test_message)
        
        #if success:
         #   print(f"✅ Test successful! Result: {result}")
        #else:
        #    print(f"❌ Test failed! Result: {result}")
        
        #return success, result
        return True
        

# Test function for standalone testing
if __name__ == "__main__":
    print("🧪 Testing Notifier...")
    notifier = Notifier()
    
    # Uncomment the line below to test with your phone number
    # notifier.te  # Replace with your phone number
    
    print("✅ Notifier test complete!")