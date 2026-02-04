#!/usr/bin/env python3
"""
Test authentication functionality
"""

from supabase_client import supabase_client
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_supabase_auth():
    """Test Supabase authentication"""
    print("🔐 Testing Supabase Authentication...")
    
    if not supabase_client.is_available():
        print("❌ Supabase not available")
        return False
    
    try:
        # Test sign up
        print("Testing sign up...")
        test_email = "test@example.com"
        test_password = "testpass123"
        
        response = supabase_client.sign_up_with_email(
            email=test_email,
            password=test_password,
            user_metadata={'full_name': 'Test User'}
        )
        
        print(f"Sign up response: {response}")
        
        if response.user:
            print(f"✅ User created: {response.user.id}")
            print(f"   Email: {response.user.email}")
            print(f"   Metadata: {response.user.user_metadata}")
        else:
            print("❌ No user in response")
        
        return True
        
    except Exception as e:
        print(f"❌ Auth test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_supabase_auth()