"""
Production-Grade Resume Generator Entry Point

This module serves as the main entry point for resume generation,
utilizing the upgraded resume_builder with ATS optimization.
"""

import logging

logger = logging.getLogger(__name__)


def generate_resume(data, style='modern'):
    """
    Generate ATS-optimized resume using production-grade builder
    
    Args:
        data (dict): Structured resume data from wizard form
        style (str): Resume style - 'simple', 'modern', or 'academic'
        
    Returns:
        str: Complete, ATS-optimized resume text
    """
    logger.info(f"Generating resume with style: {style} using production builder")
    logger.info(f"Input data keys: {list(data.keys())}")
    logger.info(f"Education entries: {len(data.get('education_entries', []))}")
    logger.info(f"Experience entries: {len(data.get('experience_entries', []))}")
    logger.info(f"Project entries: {len(data.get('project_entries', []))}")
    logger.info(f"Custom sections: {len(data.get('custom_sections', []))}")
    
    try:
        # Import here to avoid circular imports
        from .resume_builder import generate_resume as build_resume
        
        # Use the production-grade resume builder
        resume_text = build_resume(data, style)
        
        logger.info(f"Resume builder returned {len(resume_text)} characters")
        
        # Ensure we never return empty content
        if not resume_text or not resume_text.strip():
            logger.warning("Resume builder returned empty content, creating minimal fallback")
            resume_text = _create_minimal_fallback(data)
        
        logger.info("Successfully generated resume using production builder")
        return resume_text
        
    except Exception as e:
        logger.error(f"Error in resume generation: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Create fallback resume
        return _create_minimal_fallback(data)


def _create_minimal_fallback(data):
    """Create minimal fallback resume if all else fails"""
    parts = []
    
    # Name
    name = data.get('name', 'Professional Resume')
    parts.append(name.upper())
    parts.append('=' * len(name))
    parts.append('')
    
    # Contact
    contact = []
    if data.get('email'):
        contact.append(f"Email: {data['email']}")
    if data.get('phone'):
        contact.append(f"Phone: {data['phone']}")
    if data.get('location'):
        contact.append(f"Location: {data['location']}")
    if data.get('linkedin'):
        contact.append(f"LinkedIn: {data['linkedin']}")
    if data.get('website'):
        contact.append(f"Website: {data['website']}")
    
    if contact:
        parts.append(' | '.join(contact))
        parts.append('')
    
    # Basic content
    if data.get('objective'):
        parts.append('PROFESSIONAL SUMMARY')
        parts.append('-' * 30)
        parts.append(data['objective'])
        parts.append('')
    
    if data.get('skills'):
        parts.append('TECHNICAL SKILLS')
        parts.append('-' * 30)
        parts.append(data['skills'])
        parts.append('')
    
    # Education entries
    education_entries = data.get('education_entries', [])
    if education_entries:
        parts.append('EDUCATION')
        parts.append('-' * 30)
        for entry in education_entries:
            entry_parts = []
            if entry.get('degree'):
                entry_parts.append(entry['degree'])
            if entry.get('field'):
                entry_parts.append(f"in {entry['field']}")
            if entry.get('institution'):
                entry_parts.append(f"from {entry['institution']}")
            if entry.get('start') and entry.get('end'):
                entry_parts.append(f"({entry['start']} - {entry['end']})")
            elif entry.get('end'):
                entry_parts.append(f"({entry['end']})")
            
            if entry_parts:
                parts.append('• ' + ' '.join(entry_parts))
            
            if entry.get('gpa'):
                parts.append(f"  GPA: {entry['gpa']}")
            if entry.get('achievements'):
                parts.append(f"  {entry['achievements']}")
        parts.append('')
    elif data.get('education'):
        parts.append('EDUCATION')
        parts.append('-' * 30)
        parts.append(data['education'])
        parts.append('')
    
    # Experience entries
    experience_entries = data.get('experience_entries', [])
    if experience_entries:
        parts.append('PROFESSIONAL EXPERIENCE')
        parts.append('-' * 30)
        for entry in experience_entries:
            if entry.get('title') and entry.get('company'):
                job_header = f"{entry['title']} at {entry['company']}"
                if entry.get('start') and entry.get('end'):
                    job_header += f" ({entry['start']} - {entry['end']})"
                elif entry.get('start'):
                    job_header += f" ({entry['start']} - Present)"
                parts.append(f"• {job_header}")
                
                if entry.get('responsibilities'):
                    for line in entry['responsibilities'].split('\n'):
                        if line.strip():
                            parts.append(f"  • {line.strip()}")
                
                if entry.get('achievements'):
                    for line in entry['achievements'].split('\n'):
                        if line.strip():
                            parts.append(f"  • {line.strip()}")
                parts.append('')
        parts.append('')
    elif data.get('experience'):
        parts.append('PROFESSIONAL EXPERIENCE')
        parts.append('-' * 30)
        parts.append(data['experience'])
        parts.append('')
    
    # Project entries
    project_entries = data.get('project_entries', [])
    if project_entries:
        parts.append('PROJECTS')
        parts.append('-' * 30)
        for entry in project_entries:
            if entry.get('name'):
                project_header = entry['name']
                if entry.get('link'):
                    project_header += f" ({entry['link']})"
                parts.append(f"• {project_header}")
                
                if entry.get('description'):
                    parts.append(f"  {entry['description']}")
                
                if entry.get('technologies'):
                    parts.append(f"  Technologies: {entry['technologies']}")
                parts.append('')
        parts.append('')
    elif data.get('projects'):
        parts.append('PROJECTS')
        parts.append('-' * 30)
        parts.append(data['projects'])
        parts.append('')
    
    # Custom sections
    custom_sections = data.get('custom_sections', [])
    if custom_sections:
        for section in custom_sections:
            if section.get('title') and section.get('content'):
                parts.append(section['title'].upper())
                parts.append('-' * 30)
                parts.append(section['content'])
                parts.append('')
    
    return '\n'.join(parts)