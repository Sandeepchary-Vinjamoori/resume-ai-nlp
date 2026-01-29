"""
Simple runner for Resume AI - redirects to main app.py
"""

if __name__ == "__main__":
    print("🚀 Starting Resume AI application...")
    print("📄 Visit http://localhost:5000 in your browser")
    
    # Import and run the main application
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)