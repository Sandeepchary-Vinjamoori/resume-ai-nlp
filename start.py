"""
Resume AI - Production Startup Script
"""

import os
import sys

def main():
    print("🚀 Starting Resume AI - Production Grade Resume Generator")
    print("=" * 60)
    
    # Change to the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🎨 Supported styles: modern, simple, academic")
    print(f"📋 Supported formats: DOCX, PDF")
    print(f"🔧 Features: Multi-step wizard, ATS optimization, Live preview")
    print("=" * 60)
    
    # Import and run the Flask app
    try:
        from app import app, cleanup_old_files
        
        # Cleanup old files
        cleanup_old_files()
        
        print("🌐 Starting web server...")
        print("📄 Visit http://localhost:5000 in your browser")
        print("⚡ Press Ctrl+C to stop the server")
        print("=" * 60)
        
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Resume AI stopped. Thanks for using our service!")
    except Exception as e:
        print(f"❌ Error starting Resume AI: {e}")
        print("💡 Try running: python app.py")

if __name__ == "__main__":
    main()