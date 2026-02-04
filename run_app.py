#!/usr/bin/env python3
"""
Run the Resume AI app
"""

from app import app

if __name__ == "__main__":
    print("🚀 Starting Resume AI application...")
    print("📄 Visit http://localhost:5000 in your browser")
    print("🔗 Auth URLs:")
    print("   - Landing: http://localhost:5000/")
    print("   - Sign In: http://localhost:5000/auth/signin")
    print("   - Sign Up: http://localhost:5000/auth/signup")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)