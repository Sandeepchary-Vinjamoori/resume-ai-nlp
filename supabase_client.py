import os
import logging
from config import Config

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Supabase client wrapper for authentication and database operations"""
    
    def __init__(self):
        self.url = Config.SUPABASE_URL
        self.key = Config.SUPABASE_KEY
        self.service_key = Config.SUPABASE_SERVICE_KEY
        
        if not self.url or not self.key:
            logger.warning("Supabase credentials not found. Using SQLite fallback.")
            self.client = None
            self.service_client = None
        else:
            try:
                # Import here to avoid issues if supabase is not installed
                from supabase import create_client
                
                # Regular client for user operations - use minimal options
                self.client = create_client(self.url, self.key)
                
                # Service client for admin operations
                if self.service_key:
                    self.service_client = create_client(self.url, self.service_key)
                else:
                    self.service_client = None
                    
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None
                self.service_client = None
    
    def is_available(self):
        """Check if Supabase is available"""
        return self.client is not None
    
    def sign_up_with_email(self, email: str, password: str, user_metadata: dict = None):
        """Sign up user with email and password"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_metadata or {}
                }
            })
            return response
        except Exception as e:
            logger.error(f"Supabase sign up error: {e}")
            raise
    
    def sign_in_with_email(self, email: str, password: str):
        """Sign in user with email and password"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return response
        except Exception as e:
            logger.error(f"Supabase sign in error: {e}")
            raise
    
    def sign_out(self):
        """Sign out current user"""
        if not self.client:
            raise Exception("Supabase client not available")
        
        try:
            response = self.client.auth.sign_out()
            return response
        except Exception as e:
            logger.error(f"Supabase sign out error: {e}")
            raise
    
    def get_user(self):
        """Get current authenticated user"""
        if not self.client:
            return None
        
        try:
            response = self.client.auth.get_user()
            return response.user if response else None
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

# Global Supabase client instance
supabase_client = SupabaseClient()