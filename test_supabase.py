#!/usr/bin/env python3
"""
Quick test script to verify Supabase connection
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase connection and setup"""
    print("🔌 Testing Supabase connection...")
    
    # Get credentials
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    
    if not url or not key:
        print("❌ Missing Supabase credentials in .env file")
        return False
    
    try:
        # Create client
        client = create_client(url, key)
        print(f"✅ Connected to: {url}")
        
        # Test auth (this should work even without being logged in)
        user = client.auth.get_user()
        print("✅ Auth service accessible")
        
        # Test database access by trying to query (will fail if tables don't exist, but connection works)
        try:
            result = client.table('users').select('*').limit(1).execute()
            print("✅ Database tables accessible")
            print(f"   Users table exists with {len(result.data)} records")
        except Exception as e:
            if "relation \"users\" does not exist" in str(e):
                print("⚠️  Users table doesn't exist yet (will be created automatically)")
            else:
                print(f"⚠️  Database query failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def create_tables_sql():
    """Generate SQL for creating tables"""
    return """
-- Enable UUID extension
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
CREATE INDEX IF NOT EXISTS idx_resumes_updated_at ON resumes(updated_at DESC);
"""

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Resume AI - Supabase Connection Test")
    print("=" * 50)
    print()
    
    if test_supabase_connection():
        print()
        print("🎉 Supabase connection successful!")
        print()
        print("📝 Next steps:")
        print("1. Copy the SQL below and run it in your Supabase SQL Editor")
        print("2. Or just run the app - tables will be created automatically")
        print()
        print("SQL to create tables:")
        print("-" * 40)
        print(create_tables_sql())
        print("-" * 40)
    else:
        print()
        print("❌ Connection failed. Please check:")
        print("1. Your .env file has correct SUPABASE_URL and SUPABASE_KEY")
        print("2. Your Supabase project is active")
        print("3. Your internet connection is working")
        print()
        print("The app will fall back to SQLite if Supabase isn't available.")