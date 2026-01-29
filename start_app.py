#!/usr/bin/env python3
"""
Simple startup script for Resume AI application
"""

import os
import sys
import logging

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'flask',
        'reportlab',
        'python-docx'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'python-docx':
                import docx
            else:
                __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"   ❌ {module} - MISSING")
    
    optional_modules = [
        'openai',
        'spacy'
    ]
    
    print("\n🔧 Optional dependencies:")
    for module in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} - Available (enhanced features enabled)")
        except ImportError:
            print(f"   ⚠️  {module} - Not available (basic features only)")
    
    if missing_modules:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_modules)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    
    print("\n✅ All required dependencies are available!")
    return True

def main():
    """Main startup function"""
    print("🚀 Resume AI - Starting Application")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import and run the app
    try:
        from app import app
        
        print("\n🌟 Resume AI Features:")
        print("   📝 7-step wizard form")
        print("   🎨 Multiple resume styles")
        print("   📄 PDF and DOCX export")
        print("   ✏️  Edit and review functionality")
        print("   🔄 Multi-page support")
        print("   🤖 AI-enhanced content (if OpenAI API key provided)")
        
        print("\n🌐 Starting web server...")
        print("📍 Open your browser and go to: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the Flask app
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to avoid double startup messages
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Resume AI stopped. Thank you for using our service!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()