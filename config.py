import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'resume_ai_secret_key_2024_auth'
    
    # Supabase settings
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
    
    # Database settings (PostgreSQL via Supabase)
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    # Use Supabase PostgreSQL if available, otherwise SQLite
    if DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    elif SUPABASE_URL:
        # For now, use SQLite until we get the proper PostgreSQL connection string
        # You'll need to add DATABASE_URL to your .env file from Supabase dashboard
        SQLALCHEMY_DATABASE_URI = 'sqlite:///resume_ai.db'
        print("⚠️  Using SQLite fallback. Add DATABASE_URL to .env for Supabase PostgreSQL")
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///resume_ai.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # Remember me duration
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Resume settings
    SUPPORTED_STYLES = ['simple', 'modern', 'academic']
    SUPPORTED_FORMATS = ['docx', 'pdf']
    
    # Output directory
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated")