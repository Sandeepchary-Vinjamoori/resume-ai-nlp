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

@dashboard_bp.route('/save_resume', methods=['POST'])
@login_required
def save_resume():
    """Save current resume from session to database"""
    try:
        # Get resume data from session
        if 'resume_data' not in session:
            return jsonify({'success': False, 'error': 'No resume data found'})
        
        resume_data = session['resume_data']
        title = request.json.get('title', '').strip()
        
        if not title:
            return jsonify({'success': False, 'error': 'Resume title is required'})
        
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
        return jsonify({'success': False, 'error': 'Failed to save resume'})

@dashboard_bp.route('/load_resume/<int:resume_id>')
@login_required
def load_resume(resume_id):
    """Load a saved resume for editing"""
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
        
        flash(f'Loaded resume: {resume.title}', 'info')
        return redirect(url_for('home'))
        
    except Exception as e:
        flash('Error loading resume', 'error')
        return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/duplicate_resume/<int:resume_id>')
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

@dashboard_bp.route('/delete_resume/<int:resume_id>', methods=['POST'])
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

@dashboard_bp.route('/update_resume/<int:resume_id>', methods=['POST'])
@login_required
def update_resume(resume_id):
    """Update an existing resume"""
    try:
        # Get resume (ensure it belongs to current user)
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            return jsonify({'success': False, 'error': 'Resume not found'})
        
        # Get updated data from session
        if 'resume_data' not in session:
            return jsonify({'success': False, 'error': 'No resume data found'})
        
        resume_data = session['resume_data']
        
        # Update resume
        resume.content = resume_data['resume_text']
        resume.style = resume_data['style']
        resume.set_form_data(resume_data['form_data'])
        resume.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Clear editing session
        session.pop('editing_resume_id', None)
        
        return jsonify({
            'success': True, 
            'message': f'Resume "{resume.title}" updated successfully!'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to update resume'})

@dashboard_bp.route('/rename_resume/<int:resume_id>', methods=['POST'])
@login_required
def rename_resume(resume_id):
    """Rename a resume"""
    try:
        # Get resume (ensure it belongs to current user)
        resume = Resume.query.filter_by(id=resume_id, user_id=current_user.id).first()
        
        if not resume:
            return jsonify({'success': False, 'error': 'Resume not found'})
        
        new_title = request.json.get('title', '').strip()
        
        if not new_title:
            return jsonify({'success': False, 'error': 'Title cannot be empty'})
        
        # Check if title already exists for this user (excluding current resume)
        existing = Resume.query.filter_by(user_id=current_user.id, title=new_title)\
                              .filter(Resume.id != resume_id).first()
        if existing:
            return jsonify({'success': False, 'error': 'A resume with this title already exists'})
        
        old_title = resume.title
        resume.title = new_title
        resume.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Resume renamed from "{old_title}" to "{new_title}"'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to rename resume'})

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