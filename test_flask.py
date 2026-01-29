"""
Test Flask app functionality directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import json

def test_routes():
    """Test all Flask routes"""
    
    with app.test_client() as client:
        print("🧪 Testing Flask Routes\n")
        
        # Test 1: Home page
        print("1. Testing home page...")
        response = client.get('/')
        if response.status_code == 200:
            print("✅ Home page loads successfully")
        else:
            print(f"❌ Home page failed: {response.status_code}")
        
        # Test 2: Loading page
        print("\n2. Testing loading page...")
        response = client.get('/loading')
        if response.status_code == 200:
            print("✅ Loading page loads successfully")
        else:
            print(f"❌ Loading page failed: {response.status_code}")
        
        # Test 3: Generate endpoint with test data
        print("\n3. Testing generate endpoint...")
        test_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1 555-123-4567',
            'objective': 'Software engineer seeking opportunities',
            'skills': 'Python, JavaScript, React',
            'style': 'modern',
            'export_format': 'docx'
        }
        
        response = client.post('/generate', data=test_data)
        if response.status_code == 200:
            print("✅ Generate endpoint works successfully")
            print(f"Response content type: {response.content_type}")
            print(f"Response length: {len(response.data)} bytes")
        else:
            print(f"❌ Generate endpoint failed: {response.status_code}")
            print(f"Response: {response.data.decode()}")
        
        # Test 4: Preview endpoint
        print("\n4. Testing preview endpoint...")
        response = client.post('/preview', data=test_data)
        if response.status_code == 200:
            print("✅ Preview endpoint works successfully")
            try:
                data = json.loads(response.data)
                print(f"Preview success: {data.get('success')}")
                print(f"Resume text length: {len(data.get('resume_text', ''))}")
            except:
                print("Preview response is not JSON")
        else:
            print(f"❌ Preview endpoint failed: {response.status_code}")
            print(f"Response: {response.data.decode()}")

if __name__ == "__main__":
    test_routes()