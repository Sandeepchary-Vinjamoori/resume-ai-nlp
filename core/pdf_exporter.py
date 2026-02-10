"""
Simple, reliable PDF exporter for resumes with proper template formatting
"""

import os
import logging

logger = logging.getLogger(__name__)


def create_simple_pdf(resume_text, filepath):
    """Create a properly formatted PDF from resume text matching web template"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.colors import black, Color
        
        logger.info(f"Creating formatted PDF: {filepath}")
        
        # Ensure directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Create canvas
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        # Define colors to match web template
        teal_color = Color(45/255, 134/255, 89/255)  # #2d8659 - section headers
        text_color = Color(51/255, 51/255, 51/255)   # #333333 - body text
        
        # Starting position
        y_position = height - 50  # Start higher
        line_height = 14
        margin_left = 72  # 1 inch from left
        page_width = width - 144  # Available width (minus margins)
        
        lines = resume_text.split('\n')
        first_line = True
        in_contact_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines but add some space
            if not line:
                y_position -= line_height * 0.3
                continue
            
            # Skip separator lines (dashes)
            if line.startswith('-') and len(set(line.strip())) <= 2:
                continue
            
            # Clean line of problematic characters
            clean_line = ''.join(char if ord(char) < 127 else ' ' for char in line)
            clean_line = clean_line.strip()
            
            if not clean_line:
                continue
            
            # Check if we need a new page
            if y_position < 72:  # 1 inch from bottom
                c.showPage()
                y_position = height - 50
            
            try:
                if first_line:
                    # NAME - Bold, centered, larger font (matches web template)
                    c.setFont("Helvetica-Bold", 18)
                    c.setFillColor(black)
                    text_width = c.stringWidth(clean_line, "Helvetica-Bold", 18)
                    x_position = (width - text_width) / 2  # Center
                    c.drawString(x_position, y_position, clean_line)
                    first_line = False
                    in_contact_section = True
                    y_position -= line_height * 1.2
                    
                elif in_contact_section and ('|' in clean_line or '@' in clean_line or 'phone' in clean_line.lower() or 'linkedin' in clean_line.lower()):
                    # CONTACT INFO - Centered, smaller font (matches web template)
                    c.setFont("Helvetica", 11)
                    c.setFillColor(text_color)
                    text_width = c.stringWidth(clean_line, "Helvetica", 11)
                    x_position = (width - text_width) / 2  # Center
                    c.drawString(x_position, y_position, clean_line)
                    y_position -= line_height
                    
                elif _is_section_header(clean_line):
                    # SECTION HEADERS - Bold, teal color with underline (matches web template)
                    in_contact_section = False
                    y_position -= line_height * 0.5  # Extra space before section
                    
                    c.setFont("Helvetica-Bold", 12)
                    c.setFillColor(teal_color)
                    c.drawString(margin_left, y_position, clean_line.upper())
                    
                    # Add underline (matches web template)
                    c.setStrokeColor(teal_color)
                    c.setLineWidth(1)
                    text_width = c.stringWidth(clean_line.upper(), "Helvetica-Bold", 12)
                    c.line(margin_left, y_position - 3, margin_left + text_width + 20, y_position - 3)
                    
                    y_position -= line_height * 1.2
                    
                elif clean_line.startswith('•') or clean_line.startswith('-'):
                    # BULLET POINTS - Indented with proper bullets (matches web template)
                    c.setFont("Helvetica", 11)
                    c.setFillColor(text_color)
                    bullet_text = clean_line[1:].strip() if clean_line.startswith(('•', '-')) else clean_line
                    
                    # Wrap long bullet points
                    if len(bullet_text) > 80:
                        # Split into multiple lines
                        words = bullet_text.split()
                        current_line = ""
                        for word in words:
                            if len(current_line + word) < 75:
                                current_line += word + " "
                            else:
                                if current_line:
                                    c.drawString(margin_left + 16, y_position, f"• {current_line.strip()}")
                                    y_position -= line_height
                                    if y_position < 72:
                                        c.showPage()
                                        y_position = height - 50
                                current_line = word + " "
                        if current_line:
                            c.drawString(margin_left + 16, y_position, f"  {current_line.strip()}")
                    else:
                        c.drawString(margin_left + 16, y_position, f"• {bullet_text}")
                    
                    y_position -= line_height
                    
                else:
                    # REGULAR BODY TEXT - Left aligned (matches web template)
                    c.setFont("Helvetica", 11)
                    c.setFillColor(text_color)
                    
                    # Wrap long lines
                    if len(clean_line) > 85:
                        words = clean_line.split()
                        current_line = ""
                        for word in words:
                            if len(current_line + word) < 80:
                                current_line += word + " "
                            else:
                                if current_line:
                                    c.drawString(margin_left, y_position, current_line.strip())
                                    y_position -= line_height
                                    if y_position < 72:
                                        c.showPage()
                                        y_position = height - 50
                                current_line = word + " "
                        if current_line:
                            c.drawString(margin_left, y_position, current_line.strip())
                    else:
                        c.drawString(margin_left, y_position, clean_line)
                    
                    y_position -= line_height
                    
            except Exception as e:
                logger.warning(f"Error drawing line '{clean_line}': {e}")
                continue
        
        # Save the PDF
        c.save()
        
        # Verify file was created
        if os.path.exists(filepath) and os.path.getsize(filepath) > 200:
            logger.info(f"Successfully created formatted PDF: {filepath} ({os.path.getsize(filepath)} bytes)")
            return True
        else:
            logger.error("PDF file was not created properly")
            return False
            
    except Exception as e:
        logger.error(f"Error creating PDF: {e}")
        return False


def _is_section_header(line):
    """Detect section headers to match web template formatting"""
    line_lower = line.lower().strip()
    
    # Known section headers from web template
    section_headers = [
        'professional summary', 'summary', 'objective', 'professional objective',
        'skills', 'technical skills', 'core competencies', 'key skills',
        'education', 'academic background', 'educational background',
        'experience', 'professional experience', 'work experience', 'employment history',
        'projects', 'key projects', 'notable projects', 'project experience',
        'certifications', 'certificates', 'awards', 'achievements', 'accomplishments',
        'languages', 'volunteer experience', 'publications', 'research'
    ]
    
    # Check if it's a known section header or short uppercase text
    return (line_lower in section_headers or 
            (line.isupper() and len(line.split()) <= 4 and len(line) > 2 and len(line) < 50))