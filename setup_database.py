#!/usr/bin/env python3
"""
Setup database tables in Supabase
"""

from supabase_client import supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_supabase_tables():
    """Create tables in Supabase using the service client"""
    if not supabase_client.is_available():
        print("❌ Supabase not available")
        return False
    
    # SQL to create tables
    sql_commands = [
        # Enable UUID extension
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
        
        # Users table
        '''
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
        ''',
        
        # Resumes table
        '''
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
        ''',
        
        # Indexes
        'CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);',
        'CREATE INDEX IF NOT EXISTS idx_resumes_user_id ON resumes(user_id);',
        'CREATE INDEX IF NOT EXISTS idx_resumes_updated_at ON resumes(updated_at DESC);'
    ]
    
    try:
        client = supabase_client.service_client or supabase_client.client
        
        for sql in sql_commands:
            print(f"Executing: {sql[:50]}...")
            result = client.rpc('exec_sql', {'sql': sql}).execute()
            print("✅ Success")
        
        print("🎉 Database setup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\n📝 Please run this SQL manually in your Supabase SQL Editor:")
        print("\n" + "\n".join(sql_commands))
        return False

if __name__ == "__main__":
    print("🗄️  Setting up Supabase database tables...")
    setup_supabase_tables()