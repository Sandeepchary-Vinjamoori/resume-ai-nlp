from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for OAuth users
    name = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    provider = db.Column(db.String(50), default='email')  # 'email', 'google', etc.
    provider_id = db.Column(db.String(100), nullable=True)  # OAuth provider user ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with resumes
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        if password:
            self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def create_from_supabase_user(supabase_user):
        """Create User from Supabase user data"""
        user_metadata = supabase_user.user_metadata or {}
        app_metadata = supabase_user.app_metadata or {}
        
        user = User(
            id=supabase_user.id,
            email=supabase_user.email,
            name=user_metadata.get('full_name') or user_metadata.get('name') or supabase_user.email.split('@')[0],
            avatar_url=user_metadata.get('avatar_url'),
            provider=app_metadata.get('provider', 'email'),
            provider_id=app_metadata.get('provider_id')
        )
        
        return user
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'provider': self.provider,
            'created_at': self.created_at.isoformat(),
            'resume_count': len(self.resumes)
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class Resume(db.Model):
    """Resume model for storing user resumes"""
    __tablename__ = 'resumes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Generated resume text
    style = db.Column(db.String(50), nullable=False, default='modern')
    form_data = db.Column(db.Text, nullable=False)  # JSON string of form data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_form_data(self, data):
        """Store form data as JSON string"""
        self.form_data = json.dumps(data)
    
    def get_form_data(self):
        """Retrieve form data from JSON string"""
        try:
            return json.loads(self.form_data)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def to_dict(self):
        """Convert resume to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'style': self.style,
            'form_data': self.get_form_data(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Resume {self.title} by User {self.user_id}>'