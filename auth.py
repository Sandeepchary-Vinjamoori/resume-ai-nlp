from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Resume
from supabase_client import supabase_client
from werkzeug.security import generate_password_hash
import re
import logging

auth_bp = Blueprint('auth', __name__)
logger = logging.getLogger(__name__)

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, ""

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # Validation
            if not all([name, email, password, confirm_password]):
                flash('All fields are required', 'error')
                return render_template('auth/signup.html')
            
            if not is_valid_email(email):
                flash('Please enter a valid email address', 'error')
                return render_template('auth/signup.html')
            
            if password != confirm_password:
                flash('Passwords do not match', 'error')
                return render_template('auth/signup.html')
            
            is_valid, error_msg = is_valid_password(password)
            if not is_valid:
                flash(error_msg, 'error')
                return render_template('auth/signup.html')
            
            # Check if user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already registered. Please sign in instead.', 'error')
                return render_template('auth/signup.html')
            
            # Try Supabase first, then fallback to local
            if supabase_client.is_available():
                try:
                    # Sign up with Supabase
                    response = supabase_client.sign_up_with_email(
                        email=email,
                        password=password,
                        user_metadata={'full_name': name}
                    )
                    
                    if response.user:
                        # Create local user record with Supabase UUID
                        user = User(
                            id=response.user.id,  # Use Supabase UUID
                            name=name,
                            email=email,
                            provider='email'
                        )
                        # Don't set password hash for Supabase users
                        
                        db.session.add(user)
                        db.session.commit()
                        
                        # Log in the user
                        login_user(user)
                        flash(f'Welcome {name}! Your account has been created successfully.', 'success')
                        return redirect(url_for('dashboard.dashboard'))
                    else:
                        flash('Failed to create account. Please try again.', 'error')
                        
                except Exception as e:
                    logger.error(f"Supabase signup error: {e}")
                    # Fall back to local authentication
                    user = User(
                        name=name,
                        email=email,
                        provider='email'
                    )
                    user.set_password(password)
                    
                    db.session.add(user)
                    db.session.commit()
                    
                    # Log in the user
                    login_user(user)
                    flash(f'Welcome {name}! Your account has been created successfully.', 'success')
                    return redirect(url_for('dashboard.dashboard'))
            else:
                # Fallback to local authentication
                user = User(
                    name=name,
                    email=email,
                    provider='email'
                )
                user.set_password(password)
                
                db.session.add(user)
                db.session.commit()
                
                # Log in the user
                login_user(user)
                flash(f'Welcome {name}! Your account has been created successfully.', 'success')
                return redirect(url_for('dashboard.dashboard'))
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Signup error: {e}")
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/signup.html')

@auth_bp.route('/signin', methods=['GET', 'POST'])
def signin():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            remember = bool(request.form.get('remember'))
            
            if not email or not password:
                flash('Email and password are required', 'error')
                return render_template('auth/signin.html')
            
            # Try Supabase first, fallback to local
            if supabase_client.is_available():
                try:
                    response = supabase_client.sign_in_with_email(email, password)
                    
                    if response.user:
                        # Find or create local user
                        user = User.query.filter_by(email=email).first()
                        if not user:
                            # Create local user with Supabase UUID
                            user = User(
                                id=response.user.id,
                                email=email,
                                name=response.user.user_metadata.get('full_name', email.split('@')[0]),
                                provider='email'
                            )
                            db.session.add(user)
                            db.session.commit()
                        
                        login_user(user, remember=remember)
                        flash(f'Welcome back, {user.name}!', 'success')
                        
                        # Redirect to next page or dashboard
                        next_page = request.args.get('next')
                        if next_page:
                            return redirect(next_page)
                        return redirect(url_for('dashboard.dashboard'))
                    else:
                        flash('Invalid email or password', 'error')
                        
                except Exception as e:
                    logger.error(f"Supabase signin error: {e}")
                    # Try local authentication as fallback
                    user = User.query.filter_by(email=email).first()
                    if user and user.check_password(password):
                        login_user(user, remember=remember)
                        flash(f'Welcome back, {user.name}!', 'success')
                        
                        next_page = request.args.get('next')
                        if next_page:
                            return redirect(next_page)
                        return redirect(url_for('dashboard.dashboard'))
                    else:
                        flash('Invalid email or password', 'error')
            else:
                # Local authentication only
                user = User.query.filter_by(email=email).first()
                if user and user.check_password(password):
                    login_user(user, remember=remember)
                    flash(f'Welcome back, {user.name}!', 'success')
                    
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect(url_for('dashboard.dashboard'))
                else:
                    flash('Invalid email or password', 'error')
                
        except Exception as e:
            logger.error(f"Signin error: {e}")
            flash('An error occurred during sign in. Please try again.', 'error')
    
    return render_template('auth/signin.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    name = current_user.name
    
    # Sign out from Supabase if available
    if supabase_client.is_available():
        try:
            supabase_client.sign_out()
        except Exception as e:
            logger.error(f"Supabase logout error: {e}")
    
    logout_user()
    flash(f'Goodbye {name}! You have been logged out successfully.', 'info')
    return redirect(url_for('landing'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)