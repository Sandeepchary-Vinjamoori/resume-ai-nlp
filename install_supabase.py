#!/usr/bin/env python3
"""
Supabase Setup Helper for Resume AI
This script helps you set up Supabase integration quickly.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    print("=" * 60)
    print("🚀 Resume AI - Supabase Setup Helper")
    print("=" * 60)
    print()

def check_requirements():
    """Check if required packages are installed"""
    print("📦 Checking requirements...")
    
    try:
        import supabase
        print("✅ Supabase package found")
    except ImportError:
        print("❌ Supabase package not found")
        print("Installing supabase...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "supabase==2.3.4"])
        print("✅ Supabase package installed")
    
    try:
        import dotenv
        print("✅ python-dotenv package found")
    except ImportError:
        print("❌ python-dotenv package not found")
        print("Installing python-dotenv...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv==1.0.0"])
        print("✅ python-dotenv package installed")
    
    print()

def create_env_file():
    """Create .env file with Supabase configuration"""
    print("📝 Setting up environment configuration...")
    
    env_path = Path(".env")
    
    if env_path.exists():
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env file creation")
            return
    
    print("\n🔑 Please provide your Supabase credentials:")
    print("(You can find these in your Supabase dashboard → Settings → API)")
    print()
    
    supabase_url = input("Supabase Project URL: ").strip()
    supabase_key = input("Supabase Anon Key: ").strip()
    supabase_service_key = input("Supabase Service Role Key (optional): ").strip()
    
    if not supabase_url or not supabase_key:
        print("❌ URL and Anon Key are required!")
        return False
    
    # Generate a random secret key
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    env_content = f"""# Supabase Configuration
SUPABASE_URL={supabase_url}
SUPABASE_KEY={supabase_key}
SUPABASE_SERVICE_KEY={supabase_service_key}

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development

# OpenAI Configuration (if using)
OPENAI_API_KEY=your_openai_api_key_here
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created successfully!")
    print()
    return True

def test_connection():
    """Test Supabase connection"""
    print("🔌 Testing Supabase connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("❌ Missing Supabase credentials in .env file")
            return False
        
        client = create_client(url, key)
        
        # Test connection by trying to get user (will return None but shouldn't error)
        client.auth.get_user()
        
        print("✅ Supabase connection successful!")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Please check your credentials and try again.")
        print()
        return False

def setup_database():
    """Provide database setup instructions"""
    print("🗄️  Database Setup Instructions:")
    print()
    print("1. Go to your Supabase dashboard")
    print("2. Navigate to SQL Editor")
    print("3. Run the following SQL to create tables:")
    print()
    
    sql = """-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(100) NOT NULL,
    avatar_url VARCHAR(500),
    provider VARCHAR(50) DEFAULT 'email',
    provider_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Resumes table
CREATE TABLE IF NOT EXISTS resumes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    style VARCHAR(50) DEFAULT 'modern',
    form_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);
CREATE INDEX IF NOT EXISTS idx_resumes_updated_at ON resumes(updated_at DESC);"""
    
    print(sql)
    print()
    print("4. The app will also create tables automatically on first run")
    print()

def main():
    print_header()
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Please run this script from the resume_ai directory")
        print("   (where app.py is located)")
        sys.exit(1)
    
    # Step 1: Check requirements
    check_requirements()
    
    # Step 2: Create .env file
    if not create_env_file():
        print("❌ Setup failed. Please try again.")
        sys.exit(1)
    
    # Step 3: Test connection
    if not test_connection():
        print("⚠️  Connection test failed, but you can still proceed.")
        print("   The app will fall back to SQLite if Supabase isn't available.")
    
    # Step 4: Database setup instructions
    setup_database()
    
    # Final instructions
    print("🎉 Setup Complete!")
    print()
    print("Next steps:")
    print("1. Run the SQL commands above in your Supabase dashboard")
    print("2. (Optional) Set up Google OAuth in Supabase Authentication settings")
    print("3. Start your app: python app.py")
    print()
    print("📚 For detailed instructions, see SUPABASE_SETUP.md")
    print()

if __name__ == "__main__":
    main()