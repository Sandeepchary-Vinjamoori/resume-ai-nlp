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
from datetime import datetime
from io import BytesIO
import tempfile

app = Flask(__name__)
app.config.from_object(Config)

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
    
    # Convert resume text to HTML for display
    resume_html = convert_resume_to_html(resume_text, style)
    
    # Check if user is editing an existing resume
    editing_resume_id = session.get('editing_resume_id')
    
    return render_template('review.html', 
                         resume_text=resume_text,
                         resume_html=resume_html,
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
            export_to_pdf(resume_text, filepath)
            mime_type = "application/pdf"
        else:
            export_to_docx(resume_text, filepath)
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
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
        return jsonify({'success': False, 'error': str(e)})


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


def convert_resume_to_html(resume_text, style):
    """Convert plain text resume to HTML for display"""
    if not resume_text:
        return ""
    
    lines = resume_text.split('\n')
    html_parts = []
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if it's a section header (all caps or specific patterns)
        if (line.isupper() and len(line) > 2 and len(line) < 50) or \
           line in ['CONTACT INFORMATION', 'PROFESSIONAL SUMMARY', 'EDUCATION', 
                   'WORK EXPERIENCE', 'PROJECTS', 'SKILLS', 'CERTIFICATIONS']:
            current_section = line
            html_parts.append(f'<div class="resume-section">')
            html_parts.append(f'<h2 class="resume-section-title">{line}</h2>')
            continue
        
        # Skip separator lines
        if line.startswith('---') or line.startswith('===') or line.startswith('___'):
            continue
        
        # Handle different content types
        if line.startswith('•') or line.startswith('-') or line.startswith('▸'):
            html_parts.append(f'<div class="resume-bullet">{line}</div>')
        elif current_section == 'CONTACT INFORMATION' or current_section == 'CONTACT':
            html_parts.append(f'<div class="resume-contact">{line}</div>')
        elif '|' in line and current_section in ['EDUCATION', 'WORK EXPERIENCE', 'EXPERIENCE']:
            # Handle formatted entries like "Job Title | Company | Date"
            html_parts.append(f'<div class="resume-item-header">{line}</div>')
        else:
            # Regular content
            if len(line) > 100:  # Longer text, probably description
                html_parts.append(f'<div class="resume-item-content">{line}</div>')
            else:  # Shorter text, probably header or subheader
                html_parts.append(f'<div class="resume-item-subheader">{line}</div>')
    
    # Close any open section
    if current_section:
        html_parts.append('</div>')
    
    # Wrap in header if we have contact info
    html_content = '\n'.join(html_parts)
    
    # Add name header if we can extract it
    lines = resume_text.split('\n')
    name_line = None
    for line in lines[:5]:  # Check first 5 lines for name
        line = line.strip()
        if line and not line.isupper() and len(line) > 5 and len(line) < 50:
            if not any(char in line for char in ['@', 'http', '(', ')']):
                name_line = line
                break
    
    if name_line:
        html_content = f'''
        <div class="resume-header">
            <h1 class="resume-name">{name_line}</h1>
        </div>
        {html_content}
        '''
    
    return html_content


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
    """Create backward compatibility experience string"""
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
        
        if exp.get('start') and exp.get('end'):
            entry_parts.append(f"({exp['start']} - {exp['end']})")
        
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