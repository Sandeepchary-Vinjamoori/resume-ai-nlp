from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from models import db, Resume
from core.simple_builder import generate_resume
from datetime import datetime
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing all saved resumes"""
    try:
        # Get user's resumes ordered by last updated
        resumes = Resume.query.filter_by(user_id=current_user.id)\
                             .order_by(Resume.updated_at.desc())\
                             .all()
        
        # Convert to dict for template
        resume_list = []
        for resume in resumes:
            resume_dict = resume.to_dict()
            # Add preview (first 200 chars)
            resume_dict['preview'] = resume.content[:200] + '...' if len(resume.content) > 200 else resume.content
            resume_list.append(resume_dict)
        
        return render_template('dashboard/dashboard.html', 
                             resumes=resume_list,
                             user=current_user)
        
    except Exception as e:
        flash('Error loading dashboard. Please try again.', 'error')
        return redirect(url_for('landing'))

@dashboard_bp.route('/duplicate_resume/<resume_id>')
@login_required
def duplicate_resume(resume_id):
    """Duplicate an existing resume"""
    try:
        # Get original resume
        original = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not original:
            flash('Resume not found', 'error')
            return redirect(url_for('dashboard.dashboard'))
        
        # Create duplicate with new title
        duplicate_title = f"{original.title} (Copy)"
        counter = 1
        
        # Ensure unique title
        while Resume.query.filter_by(user_id=current_user.id, title=duplicate_title).first():
            counter += 1
            duplicate_title = f"{original.title} (Copy {counter})"
        
        # Create duplicate
        duplicate = Resume(
            user_id=current_user.id,
            title=duplicate_title,
            content=original.content,
            style=original.style,
            form_data=original.form_data
        )
        
        db.session.add(duplicate)
        db.session.commit()
        
        flash(f'Resume duplicated as "{duplicate_title}"', 'success')
        return redirect(url_for('dashboard.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('Error duplicating resume', 'error')
        return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/resume_stats')
@login_required
def resume_stats():
    """Get user's resume statistics"""
    try:
        total_resumes = Resume.query.filter_by(user_id=current_user.id).count()
        
        # Get style distribution
        style_stats = db.session.query(Resume.style, db.func.count(Resume.id))\
                               .filter_by(user_id=current_user.id)\
                               .group_by(Resume.style)\
                               .all()
        
        # Get recent activity (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_count = Resume.query.filter_by(user_id=current_user.id)\
                                  .filter(Resume.updated_at >= thirty_days_ago)\
                                  .count()
        
        return jsonify({
            'total_resumes': total_resumes,
            'style_distribution': dict(style_stats),
            'recent_activity': recent_count
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to get statistics'})