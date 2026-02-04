#!/usr/bin/env python3
"""
Start the Flask app with proper error handling
"""

from app import app
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        print("🚀 Starting Resume AI application...")
        print("📄 Visit http://localhost:5000 in your browser")
        print("🔗 Auth URLs:")
        print("   - Sign In: http://localhost:5000/auth/signin")
        print("   - Sign Up: http://localhost:5000/auth/signup")
        print("   - Landing: http://localhost:5000/")
        print()
        
        # Test routes before starting
        with app.test_client() as client:
            signin_test = client.get('/auth/signin')
            signup_test = client.get('/auth/signup')
            landing_test = client.get('/')
            
            print(f"✅ Route tests:")
            print(f"   - /auth/signin: {signin_test.status_code}")
            print(f"   - /auth/signup: {signup_test.status_code}")
            print(f"   - /: {landing_test.status_code}")
            print()
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.error(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()