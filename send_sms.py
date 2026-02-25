from twilio.rest import Client
from decouple import config
import os

#--------------------------------------------------------
# Twilio SMS Configuration
# Credentials loaded from .env file for security
#-------------------------------------------------------

def send(value, classes):
    """
    Send SMS notification with DR prediction results
    
    Args:
        value: Prediction severity level (0-4)
        classes: Prediction class name (e.g., "No DR", "Moderate")
    """
    try:
        # Load credentials from .env file
        account_sid = config('TWILIO_ACCOUNT_SID', default=os.getenv('TWILIO_ACCOUNT_SID'))
        auth_token = config('TWILIO_AUTH_TOKEN', default=os.getenv('TWILIO_AUTH_TOKEN'))
        from_phone = config('TWILIO_PHONE', default=os.getenv('TWILIO_PHONE'))
        to_phone = config('RECIPIENT_PHONE', default=os.getenv('RECIPIENT_PHONE'))
        
        if not all([account_sid, auth_token, from_phone, to_phone]):
            print("❌ Error: Missing Twilio credentials in .env file")
            return None
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Format phone number for Indian numbers
        if to_phone.startswith('9') and len(to_phone) == 10:
            to_phone = f"+91{to_phone}"
        
        # Create and send message
        message = client.messages.create(
            to=to_phone,
            from_=from_phone,
            body=f"Team Thiran - DR Detection Report\n\nSeverity Level: {value}\nClassification: {classes}\n\nPlease consult an ophthalmologist for confirmation."
        )
        
        print('✅ Message sent successfully!')
        print(f'Message SID: {message.sid}')
        return message.sid
        
    except Exception as e:
        print(f"❌ SMS Error: {str(e)}")
        return None

