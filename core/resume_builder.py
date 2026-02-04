"""
Production-Grade Resume Builder with ATS Optimization

FEATURES:
- ATS-first formatting with strict structure
- Linguistic transformation of content
- Professional recruiter-grade output
- Clean plain text suitable for DOCX and ATS
- Never returns empty output

ATS FORMATTING RULES:
- All section headers in UPPERCASE
- Divider line under every header  
- One blank line between sections
- No decorative characters or emojis
- Strong action verbs in every bullet
- Quantified achievements where possible

SECTION ORDER:
1. Header (Name, Contact Info)
2. Professional Summary
3. Technical Skills
4. Education  
5. Professional Experience
6. Projects
7. Custom Sections
"""

from typing import Dict, List, Any
import logging
from .content_enhancer import ContentEnhancer

logger = logging.getLogger(__name__)


def generate_resume(data: Dict[str, Any], style: str = 'modern') -> str:
    """
    Generate a complete, ATS-optimized resume from structured form data
    
    Transform: Natural Answers → Linguistic Analysis → Professional Rewrite → ATS-Optimized Resume
    
    Args:
        data (dict): Structured resume data from wizard form
        style (str): Resume style - 'simple', 'modern', or 'academic'
        
    Returns:
        str: Complete, ATS-formatted resume text (never empty)
    """
    logger.info(f"Generating ATS-optimized resume with style: {style}")
    logger.info(f"Data keys: {list(data.keys())}")
    
    # Initialize content enhancer for linguistic transformation
    enhancer = None
    try:
        enhancer = ContentEnhancer()
        logger.info("Successfully initialized content enhancer for linguistic processing")
    except Exception as e:
        logger.warning(f"Content enhancer initialization failed: {e}, using basic processing")
    
    # Build resume sections with ATS formatting
    resume_sections = []
    
    # 1. HEADER SECTION (always present)
    try:
        header_section = _build_header_section(data)
        if header_section:
            resume_sections.append(header_section)
            logger.info("Added header section")
    except Exception as e:
        logger.error(f"Error building header: {e}")
    
    # 2. PROFESSIONAL SUMMARY
    try:
        summary_section = _build_summary_section(data, enhancer)
        if summary_section:
            resume_sections.append(summary_section)
            logger.info("Added professional summary section")
    except Exception as e:
        logger.error(f"Error building summary: {e}")
    
    # 3. TECHNICAL SKILLS
    try:
        skills_section = _build_skills_section(data, enhancer)
        if skills_section:
            resume_sections.append(skills_section)
            logger.info("Added technical skills section")
    except Exception as e:
        logger.error(f"Error building skills: {e}")
    
    # 4. EDUCATION
    try:
        education_section = _build_education_section(data, enhancer)
        if education_section:
            resume_sections.append(education_section)
            logger.info("Added education section")
        else:
            logger.warning("Education section was empty")
    except Exception as e:
        logger.error(f"Error building education: {e}")
    
    # 5. PROFESSIONAL EXPERIENCE
    try:
        experience_section = _build_experience_section(data, enhancer)
        if experience_section:
            resume_sections.append(experience_section)
            logger.info("Added professional experience section")
        else:
            logger.warning("Experience section was empty")
    except Exception as e:
        logger.error(f"Error building experience: {e}")
    
    # 6. PROJECTS
    try:
        projects_section = _build_projects_section(data, enhancer)
        if projects_section:
            resume_sections.append(projects_section)
            logger.info("Added projects section")
        else:
            logger.warning("Projects section was empty")
    except Exception as e:
        logger.error(f"Error building projects: {e}")
    
    # 7. CUSTOM SECTIONS
    try:
        custom_sections = _build_custom_sections(data, enhancer)
        resume_sections.extend(custom_sections)
        if custom_sections:
            logger.info(f"Added {len(custom_sections)} custom sections")
    except Exception as e:
        logger.error(f"Error building custom sections: {e}")
    
    # Join all sections with minimal spacing (single blank line between sections)
    complete_resume = '\n'.join(resume_sections)
    
    # Ensure we never return empty content
    if not complete_resume.strip():
        logger.warning("Generated resume was empty, creating fallback resume")
        complete_resume = _create_fallback_resume(data)
    
    logger.info(f"Successfully generated ATS-optimized resume with {len(resume_sections)} sections, {len(complete_resume)} characters")
    return complete_resume.strip()


def _build_header_section(data: Dict[str, Any]) -> str:
    """Build the header section with name and contact information in professional format"""
    header_parts = []
    
    # Name (always required) - Professional format: centered, large font
    name = data.get('name', '').strip()
    if not name:
        name = 'Professional Resume'  # Fallback
    
    # Name - will be styled by CSS
    header_parts.append(name.title())
    
    # Contact information - Professional format: centered, smaller font
    contact_info = []
    
    if data.get('location'):
        contact_info.append(data['location'])
    
    if data.get('email'):
        contact_info.append(data['email'])
    
    if data.get('phone'):
        contact_info.append(data['phone'])
    
    if data.get('linkedin'):
        linkedin_url = data['linkedin']
        if not linkedin_url.startswith('http'):
            linkedin_url = f"https://{linkedin_url}"
        contact_info.append(linkedin_url)
    
    if data.get('website'):
        website_url = data['website']
        if not website_url.startswith('http'):
            website_url = f"https://{website_url}"
        contact_info.append(website_url)
    
    # Format contact info - Professional with pipe separators
    if contact_info:
        header_parts.append(' | '.join(contact_info))
    
    return '\n'.join(header_parts)


def _build_summary_section(data: Dict[str, Any], enhancer) -> str:
    """Build professional summary section with professional formatting"""
    objective = data.get('objective', '').strip()
    
    if not objective:
        return ""
    
    # Transform using linguistic processing
    if enhancer:
        try:
            enhanced_summary = enhancer.enhance_summary(objective)
        except Exception as e:
            logger.warning(f"Summary enhancement failed: {e}")
            enhanced_summary = objective
    else:
        enhanced_summary = objective
    
    # Professional format: Clean header with content and separator at end
    section_parts = []
    section_parts.append('Professional Summary')
    section_parts.append(enhanced_summary)
    section_parts.append('-' * 50)  # Shorter horizontal line
    
    return '\n'.join(section_parts)


def _build_skills_section(data: Dict[str, Any], enhancer) -> str:
    """Build technical skills section with professional formatting"""
    skills = data.get('skills', '').strip()
    
    if not skills:
        return ""
    
    # Transform using linguistic processing
    if enhancer:
        try:
            enhanced_skills = enhancer.enhance_skills(skills)
        except Exception as e:
            logger.warning(f"Skills enhancement failed: {e}")
            enhanced_skills = skills
    else:
        enhanced_skills = skills
    
    # Professional format: Clean header with content and separator at end
    section_parts = []
    section_parts.append('Skills')
    
    # Format skills as bullet points for better readability
    if '\n' in enhanced_skills:
        # Already formatted with categories
        section_parts.append(enhanced_skills)
    else:
        # Simple comma-separated skills - convert to bullets
        skill_list = [skill.strip() for skill in enhanced_skills.split(',') if skill.strip()]
        for skill in skill_list:
            section_parts.append(f'• {skill}')
    
    section_parts.append('-' * 50)  # Shorter horizontal line
    
    return '\n'.join(section_parts)


def _build_education_section(data: Dict[str, Any], enhancer) -> str:
    """Build education section with professional formatting"""
    education_entries = data.get('education_entries', [])
    
    # Fallback to legacy education field
    if not education_entries and data.get('education'):
        if enhancer:
            try:
                enhanced_education = enhancer.enhance_education(data['education'])
            except Exception as e:
                logger.warning(f"Education enhancement failed: {e}")
                enhanced_education = data['education']
        else:
            enhanced_education = data['education']
            
        if enhanced_education:
            section_parts = []
            section_parts.append('Education')
            section_parts.append(enhanced_education)
            section_parts.append('-' * 50)  # Shorter horizontal line
            return '\n'.join(section_parts)
        return ""
    
    if not education_entries:
        return ""
    
    # Process structured education entries with professional formatting
    section_parts = []
    section_parts.append('Education')
    
    for entry in education_entries:
        if not any([entry.get('institution'), entry.get('degree'), entry.get('field')]):
            continue
        
        # Format education entry - Professional style
        entry_parts = []
        
        # Degree and field on first line
        degree_field = []
        if entry.get('degree'):
            degree_field.append(entry['degree'])
        if entry.get('field'):
            degree_field.append(f"in {entry['field']}")
        
        if degree_field:
            entry_parts.append(' '.join(degree_field))
        
        # Institution and dates on second line
        institution_info = []
        if entry.get('institution'):
            institution_info.append(entry['institution'])
        
        if entry.get('start') and entry.get('end'):
            institution_info.append(f"| Graduated: {entry['end']}")
        elif entry.get('end'):
            institution_info.append(f"| Graduated: {entry['end']}")
        
        if institution_info:
            entry_parts.append(' '.join(institution_info))
        
        # Additional info (GPA, achievements)
        additional_info = []
        if entry.get('gpa'):
            additional_info.append(f"GPA: {entry['gpa']}")
        
        if entry.get('achievements'):
            achievements = entry['achievements'].strip()
            if achievements:
                additional_info.append(achievements)
        
        if additional_info:
            entry_parts.append(', '.join(additional_info))
        
        # Add formatted entry
        if entry_parts:
            section_parts.extend(entry_parts)
            section_parts.append("")  # Blank line between entries
    
    # Remove trailing blank line
    if section_parts and section_parts[-1] == "":
        section_parts.pop()
    
    # Add separator at end of section
    if len(section_parts) > 1:
        section_parts.append('-' * 50)  # Shorter horizontal line
    
    return '\n'.join(section_parts) if len(section_parts) > 2 else ""


def _build_experience_section(data: Dict[str, Any], enhancer) -> str:
    """Build professional experience section with professional formatting"""
    experience_entries = data.get('experience_entries', [])
    
    logger.info(f"Building experience section with {len(experience_entries)} entries")
    
    # Fallback to legacy experience field
    if not experience_entries and data.get('experience'):
        logger.info("Using legacy experience field")
        if enhancer:
            try:
                enhanced_experience = enhancer.enhance_experience(data['experience'])
            except Exception as e:
                logger.warning(f"Experience enhancement failed: {e}")
                enhanced_experience = data['experience']
        else:
            enhanced_experience = data['experience']
            
        if enhanced_experience:
            section_parts = []
            section_parts.append('Experience')
            section_parts.append(enhanced_experience)
            section_parts.append('-' * 50)  # Shorter horizontal line
            return '\n'.join(section_parts)
        return ""
    
    if not experience_entries:
        logger.warning("No experience entries found")
        return ""
    
    # Process structured experience entries with professional formatting
    section_parts = []
    section_parts.append('Experience')
    
    for i, entry in enumerate(experience_entries):
        logger.info(f"Processing experience entry {i+1}: {entry}")
        
        if not any([entry.get('company'), entry.get('title')]):
            logger.warning(f"Skipping experience entry {i+1} - no company or title")
            continue
        
        # Job title and company - Professional format
        job_line = []
        if entry.get('title'):
            job_line.append(entry['title'])
        if entry.get('company'):
            job_line.append(f", {entry['company']}")
        
        if job_line:
            job_header = ''.join(job_line)
            section_parts.append(job_header)
            logger.info(f"Added job header: {job_header}")
        
        # Dates on separate line
        if entry.get('start') and entry.get('end'):
            section_parts.append(f"{entry['start']} - {entry['end']}")
        elif entry.get('start'):
            section_parts.append(f"{entry['start']} - Present")
        
        # Transform responsibilities using linguistic processing
        if entry.get('responsibilities'):
            responsibilities = entry['responsibilities'].strip()
            if responsibilities:
                logger.info(f"Processing responsibilities: {responsibilities[:100]}...")
                if enhancer:
                    try:
                        enhanced_responsibilities = enhancer.enhance_experience(responsibilities)
                        # Each line should be a bullet point
                        for line in enhanced_responsibilities.split('\n'):
                            if line.strip():
                                if line.strip().startswith('•'):
                                    section_parts.append(line.strip())
                                else:
                                    section_parts.append(f"• {line.strip()}")
                    except Exception as e:
                        logger.warning(f"Responsibility enhancement failed: {e}")
                        # Fallback to original with bullets
                        for line in responsibilities.split('\n'):
                            if line.strip():
                                section_parts.append(f"• {line.strip()}")
                else:
                    # Basic bullet formatting
                    for line in responsibilities.split('\n'):
                        if line.strip():
                            section_parts.append(f"• {line.strip()}")
                logger.info("Added responsibilities")
        
        # Transform achievements using linguistic processing
        if entry.get('achievements'):
            achievements = entry['achievements'].strip()
            if achievements:
                logger.info(f"Processing achievements: {achievements[:100]}...")
                if enhancer:
                    try:
                        enhanced_achievements = enhancer.enhance_experience(achievements)
                        # Each line should be a bullet point
                        for line in enhanced_achievements.split('\n'):
                            if line.strip():
                                if line.strip().startswith('•'):
                                    section_parts.append(line.strip())
                                else:
                                    section_parts.append(f"• {line.strip()}")
                    except Exception as e:
                        logger.warning(f"Achievement enhancement failed: {e}")
                        # Fallback to original with bullets
                        for line in achievements.split('\n'):
                            if line.strip():
                                section_parts.append(f"• {line.strip()}")
                else:
                    # Basic bullet formatting
                    for line in achievements.split('\n'):
                        if line.strip():
                            section_parts.append(f"• {line.strip()}")
                logger.info("Added achievements")
        
        # Add blank line between entries for professional spacing
        section_parts.append("")
    
    # Remove trailing blank line
    if section_parts and section_parts[-1] == "":
        section_parts.pop()
    
    # Add separator at end of section
    if len(section_parts) > 1:
        section_parts.append('-' * 50)  # Shorter horizontal line
    
    result = '\n'.join(section_parts) if len(section_parts) > 2 else ""
    logger.info(f"Experience section result length: {len(result)} characters")
    return result


def _build_projects_section(data: Dict[str, Any], enhancer) -> str:
    """Build projects section with professional formatting"""
    project_entries = data.get('project_entries', [])
    
    logger.info(f"Building projects section with {len(project_entries)} entries")
    
    # Fallback to legacy projects field
    if not project_entries and data.get('projects'):
        logger.info("Using legacy projects field")
        if enhancer:
            try:
                enhanced_projects = enhancer.enhance_projects(data['projects'])
            except Exception as e:
                logger.warning(f"Project enhancement failed: {e}")
                enhanced_projects = data['projects']
        else:
            enhanced_projects = data['projects']
            
        if enhanced_projects:
            section_parts = []
            section_parts.append('Projects')
            section_parts.append(enhanced_projects)
            section_parts.append('-' * 50)  # Shorter horizontal line
            return '\n'.join(section_parts)
        return ""
    
    if not project_entries:
        logger.warning("No project entries found")
        return ""
    
    # Process structured project entries with professional formatting
    section_parts = []
    section_parts.append('Projects')
    
    for i, entry in enumerate(project_entries):
        logger.info(f"Processing project entry {i+1}: {entry}")
        
        if not any([entry.get('name'), entry.get('description')]):
            logger.warning(f"Skipping project entry {i+1} - no name or description")
            continue
        
        # Project name and dates - Professional format
        if entry.get('name'):
            project_header = entry['name']
            
            # Add dates if available (assuming project has start/end dates)
            if entry.get('start') and entry.get('end'):
                project_header += f", {entry['start']} - {entry['end']}"
            
            section_parts.append(project_header)
            logger.info(f"Added project header: {project_header}")
        
        # Transform description using linguistic processing
        if entry.get('description'):
            description = entry['description'].strip()
            if description:
                logger.info(f"Processing project description: {description[:100]}...")
                if enhancer:
                    try:
                        enhanced_description = enhancer.enhance_projects(description)
                        # Format as bullet points
                        for line in enhanced_description.split('\n'):
                            if line.strip():
                                if line.strip().startswith('•'):
                                    section_parts.append(line.strip())
                                else:
                                    section_parts.append(f"• {line.strip()}")
                    except Exception as e:
                        logger.warning(f"Project description enhancement failed: {e}")
                        section_parts.append(f"• {description}")
                else:
                    section_parts.append(f"• {description}")
                logger.info("Added description")
        
        # Technologies - Professional format
        if entry.get('technologies'):
            technologies = entry['technologies'].strip()
            if technologies:
                section_parts.append(f"• Technologies: {technologies}")
                logger.info(f"Added technologies: {technologies}")
        
        # Project link if available
        if entry.get('link'):
            section_parts.append(f"• Link: {entry['link']}")
        
        # Add blank line between projects for professional spacing
        section_parts.append("")
    
    # Remove trailing blank line
    if section_parts and section_parts[-1] == "":
        section_parts.pop()
    
    # Add separator at end of section
    if len(section_parts) > 1:
        section_parts.append('-' * 50)  # Shorter horizontal line
    
    result = '\n'.join(section_parts) if len(section_parts) > 2 else ""
    logger.info(f"Projects section result length: {len(result)} characters")
    return result


def _build_custom_sections(data: Dict[str, Any], enhancer) -> List[str]:
    """Build custom sections with professional formatting"""
    custom_sections = data.get('custom_sections', [])
    
    if not custom_sections:
        return []
    
    formatted_sections = []
    
    for section in custom_sections:
        title = section.get('title', '').strip()
        content = section.get('content', '').strip()
        
        if not title or not content:
            continue
        
        # Transform content using linguistic processing
        if enhancer:
            try:
                enhanced_content = enhancer.enhance_custom_section(title, content)
            except Exception as e:
                logger.warning(f"Custom section enhancement failed: {e}")
                enhanced_content = content
        else:
            enhanced_content = content
        
        if enhanced_content:
            section_parts = []
            
            # Professional format: Clean title with content and separator at end
            section_parts.append(title.title())  # Title case instead of uppercase
            section_parts.append(enhanced_content)
            section_parts.append('-' * 50)  # Shorter horizontal line
            
            formatted_sections.append('\n'.join(section_parts))
    
    return formatted_sections


def _create_fallback_resume(data: Dict[str, Any]) -> str:
    """Create a basic fallback resume with professional formatting if main generation fails"""
    logger.warning("Creating fallback resume due to generation failure")
    
    fallback_parts = []
    
    # Basic header - Professional format
    name = data.get('name', 'Professional Resume')
    fallback_parts.append(name.title())
    
    # Basic contact info
    contact_info = []
    if data.get('location'):
        contact_info.append(data['location'])
    if data.get('email'):
        contact_info.append(data['email'])
    if data.get('phone'):
        contact_info.append(data['phone'])
    
    if contact_info:
        fallback_parts.append(' | '.join(contact_info))
        fallback_parts.append("")
    
    # Basic sections with professional formatting
    if data.get('objective'):
        fallback_parts.append("Professional Summary")
        fallback_parts.append(data['objective'])
        fallback_parts.append("-" * 50)
        fallback_parts.append("")
    
    if data.get('skills'):
        fallback_parts.append("Skills")
        fallback_parts.append(data['skills'])
        fallback_parts.append("-" * 50)
        fallback_parts.append("")
    
    if data.get('experience'):
        fallback_parts.append("Experience")
        fallback_parts.append(data['experience'])
        fallback_parts.append("-" * 50)
        fallback_parts.append("")
    
    if data.get('education'):
        fallback_parts.append("Education")
        fallback_parts.append(data['education'])
        fallback_parts.append("-" * 50)
        fallback_parts.append("")
    
    if data.get('projects'):
        fallback_parts.append("Projects")
        fallback_parts.append(data['projects'])
        fallback_parts.append("-" * 50)
    
    return '\n'.join(fallback_parts)