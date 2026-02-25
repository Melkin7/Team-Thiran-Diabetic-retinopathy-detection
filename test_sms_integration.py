#!/usr/bin/env python3
"""
Test script to verify Twilio SMS integration
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        from decouple import config
        print("✅ decouple imported successfully")
    except ImportError as e:
        print(f"❌ decouple import failed: {e}")
        return False
    
    try:
        from twilio.rest import Client
        print("✅ twilio.rest.Client imported successfully")
    except ImportError as e:
        print(f"❌ twilio import failed: {e}")
        return False
    
    try:
        from send_sms import send
        print("✅ send_sms.send imported successfully")
    except ImportError as e:
        print(f"❌ send_sms import failed: {e}")
        return False
    
    return True

def test_env_variables():
    """Test if environment variables are loaded correctly"""
    print("\nTesting environment variables...")
    from decouple import config
    
    account_sid = config('TWILIO_ACCOUNT_SID', default=os.getenv('TWILIO_ACCOUNT_SID'))
    auth_token = config('TWILIO_AUTH_TOKEN', default=os.getenv('TWILIO_AUTH_TOKEN'))
    from_phone = config('TWILIO_PHONE', default=os.getenv('TWILIO_PHONE'))
    to_phone = config('RECIPIENT_PHONE', default=os.getenv('RECIPIENT_PHONE'))
    
    if all([account_sid, auth_token, from_phone, to_phone]):
        print(f"✅ All Twilio credentials loaded")
        print(f"   Account SID: {account_sid[:10]}...***")
        print(f"   From Phone: {from_phone}")
        print(f"   To Phone: {to_phone}")
        return True
    else:
        print("❌ Missing Twilio credentials in .env file")
        if not account_sid:
            print("   - TWILIO_ACCOUNT_SID not set")
        if not auth_token:
            print("   - TWILIO_AUTH_TOKEN not set")
        if not from_phone:
            print("   - TWILIO_PHONE not set")
        if not to_phone:
            print("   - RECIPIENT_PHONE not set")
        return False

def test_sms_send():
    """Test SMS sending functionality"""
    print("\nTesting SMS sending...")
    try:
        from send_sms import send
        
        print("Attempting to send test SMS...")
        result = send(2, "Moderate")
        
        if result:
            print(f"✅ SMS sent successfully!")
            print(f"   Message SID: {result}")
            return True
        else:
            print("❌ SMS sending returned None")
            return False
    except Exception as e:
        print(f"❌ SMS sending failed: {str(e)}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("Team Thiran - SMS Integration Test")
    print("="*60)
    
    # Run tests
    imports_ok = test_imports()
    
    if imports_ok:
        env_ok = test_env_variables()
        
        if env_ok:
            print("\n" + "="*60)
            print("All prerequisites met. SMS functionality ready!")
            print("="*60)
            
            # Prompt user to send test SMS
            user_choice = input("\nDo you want to send a test SMS? (yes/no): ").strip().lower()
            if user_choice == 'yes':
                sms_ok = test_sms_send()
                if sms_ok:
                    print("\n✅ SMS integration is fully functional!")
                else:
                    print("\n⚠️  SMS sending encountered issues. Check credentials.")
            else:
                print("\nSkipping SMS send test.")
        else:
            print("\n❌ Environment variables not configured. Please set .env file.")
    else:
        print("\n❌ Required packages not installed. Run: pip install -r requirements.txt")
