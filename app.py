from flask import Flask, render_template, request, send_file, jsonify, flash, session, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from core.simple_builder import generate_resume
from core.simple_exporter import export_to_docx, export_to_pdf
from config import Config
from models import db, User, Resume
from auth import auth_bp
from dashboard import dashboard_bp

import os
import uuid
import logging
import re
from datetime import datetime
from io import BytesIO
import tempfile

app = Flask(__name__)
app.config.from_object(Config)

# Add custom Jinja2 filter for regex
@app.template_filter('regex_search')
def regex_search(text, pattern):
    """Custom Jinja2 filter for regex search"""
    return bool(re.search(pattern, text))

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.signin'
login_manager.login_message = 'Please sign in to access this page.'
login_manager.login_message_category = 'info'

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp)

@login_manager.user_loader
def load_user(user_id):
    # Handle UUID strings (from Supabase) - don't convert to int
    return User.query.get(user_id)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OUTPUT_DIR = app.config['OUTPUT_DIR']
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Supported styles and formats
SUPPORTED_STYLES = app.config['SUPPORTED_STYLES']
SUPPORTED_FORMATS = app.config['SUPPORTED_FORMATS']

# Create database tables
with app.app_context():
    db.create_all()


@app.route("/health")
def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.route("/")
def landing():
    """Landing page"""
    return render_template("landing.html")


@app.route("/form", methods=["GET", "POST"])
def home():
    """Resume form page"""
    if request.method == "POST":
        # This is now just for the old form compatibility
        # The new wizard uses JavaScript to redirect to loading page
        return render_template("index.html")
    
    return render_template("index.html")


@app.route("/review")
def review():
    """Show resume review page"""
    if 'resume_data' not in session:
        flash("No resume data found. Please generate a resume first.", "error")
        return redirect(url_for('home'))
    
    resume_data = session['resume_data']
    resume_text = resume_data['resume_text']
    style = resume_data['style']
    
    # Check if user is editing an existing resume
    editing_resume_id = session.get('editing_resume_id')
    
    return render_template('review_simple.html', 
                         resume_text=resume_text,
                         style=style,
                         user=current_user,
                         editing_resume_id=editing_resume_id)


@app.route("/update_resume", methods=["POST"])
def update_resume():
    """Update resume content"""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        style = data.get('style', 'modern')
        
        if not resume_text.strip():
            return jsonify({'success': False, 'error': 'Resume text cannot be empty'})
        
        # Update session data
        if 'resume_data' in session:
            session['resume_data']['resume_text'] = resume_text
            session['resume_data']['style'] = style
        
        # Convert to HTML for display
        resume_html = convert_resume_to_html(resume_text, style)
        
        return jsonify({
            'success': True,
            'resume_html': resume_html
        })
        
    except Exception as e:
        logger.error(f"Error updating resume: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route("/change_style", methods=["POST"])
def change_style():
    """Change resume style"""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        style = data.get('style', 'modern')
        
        if style not in SUPPORTED_STYLES:
            style = 'modern'
        
        # Update session data
        if 'resume_data' in session:
            session['resume_data']['style'] = style
        
        # Convert to HTML with new style
        resume_html = convert_resume_to_html(resume_text, style)
        
        return jsonify({
            'success': True,
            'resume_html': resume_html
        })
        
    except Exception as e:
        logger.error(f"Error changing style: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route("/download_resume", methods=["POST"])
def download_resume():
    """Download resume in specified format"""
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        style = data.get('style', 'modern')
        format_type = data.get('format', 'docx')
        
        if not resume_text.strip():
            return jsonify({'success': False, 'error': 'Resume text cannot be empty'})
        
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{style}_{timestamp}.{format_type}"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Export to selected format
        if format_type == "pdf":
            # Use NUCLEAR LEFT ALIGNMENT PDF export
            try:
                from core.simple_pdf import create_simple_pdf
                logger.info("🎯 Using NUCLEAR LEFT ALIGNMENT PDF export")
                success = create_simple_pdf(resume_text, filepath)
                
                if not success:
                    # Final fallback to original PDF export
                    logger.warning("Nuclear PDF failed, using original export")
                    export_to_pdf(resume_text, filepath)
                else:
                    logger.info("✅ Nuclear PDF created successfully - FORCED LEFT ALIGNMENT")
                    
            except Exception as e:
                logger.error(f"Nuclear PDF failed: {e}, using fallback")
                export_to_pdf(resume_text, filepath)
            mime_type = "application/pdf"
        else:
            export_to_docx(resume_text, filepath)
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # Verify file exists
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            return jsonify({'success': False, 'error': 'File generation failed'})
        
        # Get clean name for download
        form_data = session.get('resume_data', {}).get('form_data', {})
        name = form_data.get('name', 'Resume')
        clean_name = name.replace(' ', '_').replace('.', '')
        download_name = f"{clean_name}_Resume.{format_type}"
        
        return send_file(
            filepath,
            as_attachment=True,
            mimetype=mime_type,
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        return jsonify({'success': False, 'error': f'Download failed: {str(e)}'})


@app.route("/regenerate_resume", methods=["POST"])
def regenerate_resume():
    """Regenerate resume using stored form data"""
    try:
        if 'resume_data' not in session:
            return jsonify({'success': False, 'error': 'No resume data found'})
        
        resume_data = session['resume_data']
        form_data = resume_data.get('form_data', {})
        style = resume_data.get('style', 'modern')
        
        # Regenerate resume
        new_resume_text = generate_resume(form_data, style)
        
        if not new_resume_text or not new_resume_text.strip():
            return jsonify({'success': False, 'error': 'Failed to regenerate resume'})
        
        # Update session
        session['resume_data']['resume_text'] = new_resume_text
        
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error regenerating resume: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@app.route("/save_resume", methods=["POST"])
def save_resume():
    """Save current resume - handles both authenticated and unauthenticated users"""
    try:
        # Check if user is authenticated
        if not current_user.is_authenticated:
            return jsonify({'success': False, 'error': 'Please login to save resumes'})
        
        # Get resume data from request (for review page) or session (for dashboard)
        data = request.get_json()
        if data and 'resume_text' in data:
            # Direct save from review page
            title = data.get('title', '').strip()
            resume_text = data.get('resume_text', '')
            style = data.get('style', 'modern')
            
            if not title:
                return jsonify({'success': False, 'error': 'Resume title is required'})
            
            if not resume_text.strip():
                return jsonify({'success': False, 'error': 'Resume content cannot be empty'})
            
            # Check if title already exists for this user
            existing = Resume.query.filter_by(user_id=current_user.id, title=title).first()
            if existing:
                return jsonify({'success': False, 'error': 'A resume with this title already exists'})
            
            # Create new resume
            resume = Resume(
                user_id=current_user.id,
                title=title,
                content=resume_text,
                style=style
            )
            
            # Try to get form data from session if available
            if 'resume_data' in session and 'form_data' in session['resume_data']:
                resume.set_form_data(session['resume_data']['form_data'])
            
            db.session.add(resume)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Resume "{title}" saved successfully!',
                'resume_id': resume.id
            })
        
        # Original session-based save logic for backward compatibility
        if 'resume_data' not in session:
            return jsonify({'success': False, 'error': 'No resume data found'})
        
        resume_data = session['resume_data']
        title = request.json.get('title', '').strip()
        
        if not title:
            return jsonify({'success': False, 'error': 'Resume title is required'})
        
        # Check if we're updating an existing resume
        editing_resume_id = session.get('editing_resume_id')
        
        if editing_resume_id:
            # Update existing resume
            resume = Resume.query.filter_by(id=editing_resume_id, user_id=current_user.id).first()
            if not resume:
                return jsonify({'success': False, 'error': 'Resume not found'})
            
            resume.content = resume_data['resume_text']
            resume.style = resume_data['style']
            resume.set_form_data(resume_data['form_data'])
            resume.updated_at = datetime.utcnow()
            
            # Clear editing session
            session.pop('editing_resume_id', None)
            
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Resume "{resume.title}" updated successfully!',
                'resume_id': resume.id
            })
        else:
            # Check if title already exists for this user
            existing = Resume.query.filter_by(user_id=current_user.id, title=title).first()
            if existing:
                return jsonify({'success': False, 'error': 'A resume with this title already exists'})
            
            # Create new resume
            resume = Resume(
                user_id=current_user.id,
                title=title,
                content=resume_data['resume_text'],
                style=resume_data['style']
            )
            resume.set_form_data(resume_data['form_data'])
            
            db.session.add(resume)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Resume "{title}" saved successfully!',
                'resume_id': resume.id
            })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving resume: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to save resume'})


@app.route("/get_resume_content/<resume_id>")
@login_required
def get_resume_content(resume_id):
    """Get resume content for viewing in dashboard"""
    try:
        # Get resume (ensure it belongs to current user)
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            return jsonify({'success': False, 'error': 'Resume not found'})
        
        # Format the resume content using the same logic as review page
        formatted_html = format_resume_for_display(resume.content)
        
        return jsonify({
            'success': True,
            'content': resume.content,
            'formatted_html': formatted_html,
            'title': resume.title,
            'style': resume.style
        })
        
    except Exception as e:
        logger.error(f"Error fetching resume content: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch resume content'})


def format_resume_for_display(resume_text):
    """Format resume text using the same logic as the review template"""
    if not resume_text:
        return '<div style="text-align: center; padding: 40px; color: #666;"><h3>No Resume Content</h3></div>'
    
    lines = resume_text.split('\n')
    html_parts = []
    
    for i, line in enumerate(lines):
        trimmed = line.strip()
        
        if not trimmed:
            # Empty line - add minimal spacing
            html_parts.append('<div class="empty-line" style="height: 2px; margin: 0;"></div>')
            continue
        
        # Name - first line
        if i == 0 and '|' not in trimmed and '@' not in trimmed:
            html_parts.append(f'<div class="name">{line}</div>')
        
        # Contact info
        elif ('|' in trimmed or '@' in trimmed or 
              (len(trimmed) > 8 and re.search(r'\d{10}', trimmed))):
            # Only center if it's actually contact info (not education with pipes)
            if not any(word in trimmed.lower() for word in ['university', 'college', 'gpa', 'bachelor', 'master', 'degree', 'engineering', 'science', 'technology', 'intermediate']):
                html_parts.append(f'<div class="contact">{line}</div>')
            else:
                html_parts.append(f'<div class="content" style="text-align: left !important;">{line}</div>')
        
        # Section headers - using the exact same logic as review template
        elif (trimmed.upper() in ['PROFESSIONAL SUMMARY', 'SUMMARY', 'SKILLS', 'EDUCATION', 'EXPERIENCE', 'PROJECTS', 'CERTIFICATIONS', 'ACHIEVEMENTS', 'AWARDS', 'PUBLICATIONS', 'LANGUAGES', 'INTERESTS', 'HOBBIES', 'VOLUNTEER', 'LEADERSHIP', 'ACTIVITIES', 'HONORS'] or
              'SUMMARY' in trimmed.upper() or 'EDUCATION' in trimmed.upper() or 
              'EXPERIENCE' in trimmed.upper() or 'PROJECTS' in trimmed.upper() or 
              'SKILLS' in trimmed.upper() or
              (trimmed.endswith(':') and len(trimmed) < 50 and len(trimmed.split()) <= 4 and trimmed.count(':') == 1 and ',' not in trimmed and 'programming' not in trimmed.lower() and 'frameworks' not in trimmed.lower() and 'databases' not in trimmed.lower() and 'cloud' not in trimmed.lower() and 'tools' not in trimmed.lower() and 'soft' not in trimmed.lower()) or
              (trimmed.isupper() and len(trimmed) > 2 and len(trimmed) < 50 and len(trimmed.split()) <= 4 and trimmed.isalpha() and ':' not in trimmed and ',' not in trimmed) or
              (len(trimmed.split()) == 1 and trimmed.istitle() and len(trimmed) > 3 and len(trimmed) < 30 and trimmed.isalpha() and ':' not in trimmed and ',' not in trimmed)):
            html_parts.append(f'<div class="section">{line}</div>')
        
        # Skip horizontal lines
        elif trimmed.startswith('-') and trimmed.replace('-', '').strip() == '':
            continue
        
        # Bullet points
        elif trimmed.startswith('•') or trimmed.startswith('-') or trimmed.startswith('*'):
            html_parts.append(f'<div class="bullet">{line}</div>')
        
        # All other content
        else:
            html_parts.append(f'<div class="content" style="text-align: left !important;">{line}</div>')
    
    return '\n'.join(html_parts)


@app.route("/store_temp_resume", methods=["POST"])
def store_temp_resume():
    """Store resume temporarily for unauthenticated users"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        style = data.get('style', 'modern')
        title = data.get('title', '').strip()
        
        if not content:
            return jsonify({'success': False, 'error': 'Resume content cannot be empty'})
        
        # Store in session for after authentication
        session['temp_resume'] = {
            'content': content,
            'style': style,
            'title': title,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info("Temporary resume stored in session")
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error storing temp resume: {e}")
        return jsonify({'success': False, 'error': 'Failed to store resume'})


@app.route("/save_temp_resume_after_auth")
@login_required
def save_temp_resume_after_auth():
    """Save temporarily stored resume after user authentication"""
    try:
        temp_resume = session.get('temp_resume')
        
        if not temp_resume:
            flash("No resume found to save.", "error")
            return redirect(url_for('review'))
        
        title = temp_resume.get('title', '').strip()
        content = temp_resume.get('content', '').strip()
        style = temp_resume.get('style', 'modern')
        
        if not title or not content:
            flash("Invalid resume data.", "error")
            return redirect(url_for('review'))
        
        # Check if title already exists for this user
        existing = Resume.query.filter_by(user_id=current_user.id, title=title).first()
        if existing:
            # Add timestamp to make it unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            title = f"{title}_{timestamp}"
        
        # Create new resume
        resume = Resume(
            user_id=current_user.id,
            title=title,
            content=content,
            style=style
        )
        
        db.session.add(resume)
        db.session.commit()
        
        # Clear temp resume from session
        session.pop('temp_resume', None)
        
        flash(f'Resume "{title}" saved successfully!', 'success')
        return redirect(url_for('review'))
        
    except Exception as e:
        logger.error(f"Error saving temp resume after auth: {e}")
        flash("Error saving resume.", "error")
        return redirect(url_for('review'))


@app.route("/edit_resume/<resume_id>")
@login_required
def edit_resume(resume_id):
    """Edit an existing resume - show edit interface directly"""
    try:
        # Get resume (ensure it belongs to current user)
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            flash('Resume not found', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        # Load resume data into session
        session['resume_data'] = {
            'resume_text': resume.content,
            'style': resume.style,
            'form_data': resume.get_form_data()
        }
        
        # Store resume ID for updating
        session['editing_resume_id'] = resume_id
        
        # Render the edit template directly (same as review but starts in edit mode)
        return render_template('edit_resume.html', 
                             resume_text=resume.content,
                             resume_html=convert_resume_to_html(resume.content, resume.style),
                             style=resume.style,
                             user=current_user,
                             editing_resume_id=resume_id,
                             resume_title=resume.title)
        
    except Exception as e:
        flash('Error loading resume for editing', 'error')
        return redirect(url_for('dashboard.dashboard'))


@app.route("/download_resume_file/<resume_id>")
@login_required
def download_resume_file(resume_id):
    """Download a saved resume file as PDF"""
    try:
        # Get resume (ensure it belongs to current user)
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            flash('Resume not found', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        # Validate resume content
        if not resume.content or not resume.content.strip():
            flash('Resume content is empty', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        # Create temporary file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{resume.style}_{timestamp}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Use the EXACT SAME export method as review page
        try:
            # Use NUCLEAR LEFT ALIGNMENT PDF export (same as review page)
            from core.simple_pdf import create_simple_pdf
            logger.info("🎯 Using NUCLEAR LEFT ALIGNMENT PDF export (same as review page)")
            success = create_simple_pdf(resume.content, filepath)
            
            if not success:
                # Final fallback to original PDF export
                logger.warning("Nuclear PDF failed, using original export")
                export_to_pdf(resume.content, filepath)
            else:
                logger.info("✅ Nuclear PDF created successfully - FORCED LEFT ALIGNMENT")
                
        except Exception as e:
            logger.error(f"Nuclear PDF failed: {e}, using fallback")
            export_to_pdf(resume.content, filepath)
        
        # Verify file was created successfully
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            raise Exception("PDF file was not created successfully or is empty")
        
        # Get clean name for download
        form_data = resume.get_form_data()
        name = form_data.get('name', resume.title)
        # Clean filename more thoroughly
        clean_name = ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        clean_name = clean_name.replace(' ', '_')[:50]  # Limit length
        if not clean_name:
            clean_name = "Resume"
        download_name = f"{clean_name}.pdf"
        
        # Clean up old files (optional - keep last 10 files)
        try:
            import glob
            old_files = glob.glob(os.path.join(OUTPUT_DIR, "resume_*.pdf"))
            old_files.sort(key=os.path.getctime)
            for old_file in old_files[:-10]:  # Keep last 10 files
                try:
                    os.remove(old_file)
                except:
                    pass
        except:
            pass
        
        return send_file(
            filepath,
            as_attachment=True,
            mimetype="application/pdf",
            download_name=download_name
        )
        
    except Exception as e:
        logger.error(f"Error downloading resume: {str(e)}")
        flash('Error downloading resume. Please try again.', 'error')
        return redirect(url_for('dashboard.dashboard'))


@app.route("/delete_resume/<resume_id>", methods=["POST"])
@login_required
def delete_resume(resume_id):
    """Delete a resume"""
    try:
        # Get resume (ensure it belongs to current user)
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            return jsonify({'success': False, 'error': 'Resume not found'})
        
        title = resume.title
        db.session.delete(resume)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Resume "{title}" deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to delete resume'})


@app.route("/update_resume/<resume_id>", methods=["POST"])
@login_required
def update_existing_resume(resume_id):
    """Update an existing resume from the edit page"""
    try:
        # Get resume (ensure it belongs to current user)
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            return jsonify({'success': False, 'error': 'Resume not found'})
        
        # Get updated data from request or session
        data = request.get_json()
        if data and 'resume_text' in data:
            # Direct update from edit page
            resume_text = data.get('resume_text', '')
            style = data.get('style', resume.style)
            
            if not resume_text.strip():
                return jsonify({'success': False, 'error': 'Resume content cannot be empty'})
            
            # Update resume
            resume.content = resume_text
            resume.style = style
            resume.updated_at = datetime.utcnow()
            
            # Also update session if it exists
            if 'resume_data' in session:
                session['resume_data']['resume_text'] = resume_text
                session['resume_data']['style'] = style
        else:
            # Update from session (for review page compatibility)
            if 'resume_data' not in session:
                return jsonify({'success': False, 'error': 'No resume data found'})
            
            resume_data = session['resume_data']
            resume.content = resume_data['resume_text']
            resume.style = resume_data['style']
            resume.set_form_data(resume_data['form_data'])
            resume.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Resume "{resume.title}" updated successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating resume: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update resume'})


def convert_resume_to_html(resume_text, style):
    """Convert plain text resume to HTML for display - matches review template CSS classes"""
    if not resume_text:
        return ""
    
    lines = resume_text.split('\n')
    html_parts = []
    
    for i, line in enumerate(lines):
        original_line = line
        trimmed = line.strip()
        
        if not trimmed:
            html_parts.append('<br>')
            continue
        
        # Name - first line (same logic as template)
        if i == 0 and '|' not in trimmed and '@' not in trimmed:
            html_parts.append(f'<div class="name">{original_line}</div>')
        # Contact info (same logic as template)
        elif '|' in trimmed or '@' in trimmed or (len(trimmed) > 8 and re.search(r'\d{10}', trimmed)):
            html_parts.append(f'<div class="contact">{original_line}</div>')
        # Section headers (same logic as template)
        elif (trimmed.upper() in ['PROFESSIONAL SUMMARY', 'SUMMARY', 'SKILLS', 'EDUCATION', 'EXPERIENCE', 'PROJECTS', 'CERTIFICATIONS'] or
              'SUMMARY' in trimmed.upper() or 'EDUCATION' in trimmed.upper() or 
              'EXPERIENCE' in trimmed.upper() or 'PROJECTS' in trimmed.upper() or 
              'SKILLS' in trimmed.upper()):
            html_parts.append(f'<div class="section">{original_line}</div>')
        # Skip horizontal lines
        elif trimmed.startswith('-') and trimmed.replace('-', '').strip() == '':
            continue
        # Bullet points (same logic as template)
        elif trimmed.startswith('•') or trimmed.startswith('-') or trimmed.startswith('*'):
            html_parts.append(f'<div class="bullet">{original_line}</div>')
        else:
            # All other content (same logic as template) - ensure left alignment
            html_parts.append(f'<div class="content">{original_line}</div>')
    
    return '\n'.join(html_parts)


@app.route("/loading")
def loading():
    """Show loading page while resume is being generated"""
    return render_template("loading.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Generate resume and redirect to review page"""
    try:
        logger.info("Generate route called")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Form data keys: {list(request.form.keys())}")
        
        # Fast data extraction using optimized function
        data = extract_form_data_optimized(request.form)
        
        logger.info(f"Form data extracted: {len(data)} fields")
        logger.info(f"Education entries: {len(data.get('education_entries', []))}")
        logger.info(f"Experience entries: {len(data.get('experience_entries', []))}")
        logger.info(f"Project entries: {len(data.get('project_entries', []))}")
        
        # Quick validation
        if not all([data.get("name"), data.get("email"), data.get("phone")]):
            logger.warning("Missing required fields")
            flash("Please fill in all required fields (Name, Email, Phone)", "error")
            return render_template("index.html")
        
        # Get style with default
        style = request.form.get("style", "modern").strip().lower()
        if style not in SUPPORTED_STYLES:
            style = "modern"

        logger.info(f"Generating resume with style: {style}")
        
        # Generate resume text (this is the main processing step)
        resume_text = generate_resume(data, style)
        
        logger.info(f"Generated resume length: {len(resume_text)} characters")
        
        if not resume_text or not resume_text.strip():
            logger.error("Resume generation returned empty content")
            flash("Failed to generate resume content. Please try again.", "error")
            return render_template("index.html")

        # Store in session for review page
        session['resume_data'] = {
            'resume_text': resume_text,
            'style': style,
            'form_data': data
        }
        
        logger.info("Resume data stored in session, redirecting to review page")
        
        # Redirect to review page
        return redirect(url_for('review'))

    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        flash("An error occurred while generating your resume. Please try again.", "error")
        return render_template("index.html")


@app.route("/preview", methods=["POST"])
def preview_resume():
    """Generate a preview of the resume - Optimized for speed"""
    try:
        # Fast data extraction
        data = extract_form_data_optimized(request.form)
        
        # Debug logging
        logger.info(f"Preview data received:")
        logger.info(f"  - Name: {data.get('name')}")
        logger.info(f"  - Education entries: {len(data.get('education_entries', []))}")
        logger.info(f"  - Experience entries: {len(data.get('experience_entries', []))}")
        logger.info(f"  - Project entries: {len(data.get('project_entries', []))}")
        logger.info(f"  - Custom sections: {len(data.get('custom_sections', []))}")
        
        # Log first few form keys for debugging
        form_keys = list(request.form.keys())[:20]
        logger.info(f"First 20 form keys: {form_keys}")
        
        # Get style with default
        style = request.form.get("style", "modern").strip().lower()
        if style not in SUPPORTED_STYLES:
            style = "modern"
        
        # Generate resume text (optimized for preview)
        resume_text = generate_resume(data, style)
        
        logger.info(f"Generated resume length: {len(resume_text)} characters")
        logger.info(f"Resume preview (first 500 chars): {resume_text[:500]}...")
        
        return jsonify({
            "success": True,
            "resume_text": resume_text,
            "style": style
        })
        
    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            "success": False,
            "error": "Failed to generate preview"
        }), 500


def extract_form_data_optimized(form_data):
    """Optimized form data extraction for better performance"""
    # Basic data extraction
    data = {
        "name": form_data.get("name", "").strip(),
        "email": form_data.get("email", "").strip(),
        "phone": form_data.get("phone", "").strip(),
        "location": form_data.get("location", "").strip(),
        "linkedin": form_data.get("linkedin", "").strip(),
        "website": form_data.get("website", "").strip(),
        "objective": form_data.get("objective", "").strip(),
        "skills": form_data.get("skills", "").strip(),
    }
    
    # Extract structured entries efficiently
    education_entries = extract_entries(form_data, "education", 
        ["institution", "degree", "field", "start", "end", "gpa", "achievements"])
    
    experience_entries = extract_entries(form_data, "experience",
        ["company", "title", "start", "end", "responsibilities", "achievements"])
    
    project_entries = extract_entries(form_data, "project",
        ["name", "description", "technologies", "link"])
    
    custom_sections = extract_entries(form_data, "custom",
        ["title", "content"])
    
    # Add to data
    data['education_entries'] = education_entries
    data['experience_entries'] = experience_entries  
    data['project_entries'] = project_entries
    data['custom_sections'] = custom_sections
    
    # Create backward compatibility strings efficiently
    data['education'] = create_education_string(education_entries)
    data['experience'] = create_experience_string(experience_entries)
    data['projects'] = create_projects_string(project_entries)
    
    return data


def extract_entries(form_data, entry_type, fields):
    """Generic function to extract structured entries efficiently"""
    entries = []
    i = 1
    
    while i <= 20:  # Reasonable limit to prevent infinite loops
        entry = {}
        has_data = False
        
        for field in fields:
            key = f"{entry_type}_{field}_{i}"
            value = form_data.get(key, "").strip()
            entry[field] = value
            if value:
                has_data = True
        
        if has_data:
            entries.append(entry)
        else:
            break
        i += 1
    
    return entries


def create_education_string(education_entries):
    """Create backward compatibility education string"""
    if not education_entries:
        return ""
    
    parts = []
    for edu in education_entries:
        entry_parts = []
        if edu.get('degree'):
            entry_parts.append(edu['degree'])
        if edu.get('field'):
            entry_parts.append(f"in {edu['field']}")
        if edu.get('institution'):
            entry_parts.append(f"from {edu['institution']}")
        if edu.get('start') and edu.get('end'):
            entry_parts.append(f"({edu['start']}-{edu['end']})")
        elif edu.get('end'):
            entry_parts.append(f"({edu['end']})")
        
        if entry_parts:
            parts.append(" ".join(entry_parts))
    
    return "; ".join(parts)


def create_experience_string(experience_entries):
    """Create backward compatibility experience string with proper date handling"""
    if not experience_entries:
        return ""
    
    parts = []
    for exp in experience_entries:
        entry_parts = []
        if exp.get('title') and exp.get('company'):
            entry_parts.append(f"{exp['title']} at {exp['company']}")
        elif exp.get('title'):
            entry_parts.append(exp['title'])
        elif exp.get('company'):
            entry_parts.append(exp['company'])
        
        # Fix: Handle all date scenarios properly
        if exp.get('start') and exp.get('end'):
            # Handle "Present" case and regular end dates
            end_date = exp['end'].strip()
            if end_date.lower() in ['present', 'current', 'ongoing']:
                entry_parts.append(f"({exp['start']} - Present)")
            else:
                entry_parts.append(f"({exp['start']} - {end_date})")
        elif exp.get('start'):
            # Only start date provided, assume current role
            entry_parts.append(f"({exp['start']} - Present)")
        elif exp.get('end'):
            # Only end date provided
            entry_parts.append(f"({exp['end']})")
        
        if exp.get('responsibilities'):
            entry_parts.append(f": {exp['responsibilities']}")
        
        if exp.get('achievements'):
            entry_parts.append(f"Achievements: {exp['achievements']}")
        
        if entry_parts:
            parts.append(" ".join(entry_parts))
    
    return "\n".join(parts)


def create_projects_string(project_entries):
    """Create backward compatibility projects string"""
    if not project_entries:
        return ""
    
    parts = []
    for proj in project_entries:
        entry_parts = []
        if proj.get('name'):
            entry_parts.append(proj['name'])
        if proj.get('description'):
            entry_parts.append(f"- {proj['description']}")
        if proj.get('technologies'):
            entry_parts.append(f"Technologies: {proj['technologies']}")
        if proj.get('link'):
            entry_parts.append(f"Link: {proj['link']}")
        
        if entry_parts:
            parts.append(" ".join(entry_parts))
    
    return "\n".join(parts)


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "supported_styles": SUPPORTED_STYLES,
        "supported_formats": SUPPORTED_FORMATS
    })


@app.errorhandler(404)
def not_found_error(error):
    return render_template("index.html"), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    flash("An internal error occurred. Please try again.", "error")
    return render_template("index.html"), 500


# Cleanup old files on startup
def cleanup_old_files():
    """Remove files older than 1 hour from the output directory"""
    try:
        import time
        current_time = time.time()
        for filename in os.listdir(OUTPUT_DIR):
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getctime(filepath)
                if file_age > 3600:  # 1 hour in seconds
                    os.remove(filepath)
                    logger.info(f"Cleaned up old file: {filename}")
    except Exception as e:
        logger.warning(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    # Cleanup old files on startup
    cleanup_old_files()
    
    print("🚀 Starting Resume AI application...")
    print("📄 Visit http://localhost:5000 in your browser")
    print(f"📁 Generated files will be saved to: {os.path.abspath(OUTPUT_DIR)}")
    print(f"🎨 Supported styles: {', '.join(SUPPORTED_STYLES)}")
    print(f"📋 Supported formats: {', '.join(SUPPORTED_FORMATS)}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)