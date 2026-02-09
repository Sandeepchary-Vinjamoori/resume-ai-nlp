"""
Simple PDF Export - Clean and reliable PDF generation with proper alignment
"""

import os
import logging

logger = logging.getLogger(__name__)


def create_simple_pdf(resume_text, filepath):
    """Create PDF with FORCED left alignment - no centering except name/contact"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import black, Color
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        
        logger.info(f"🎯 Creating PDF with NUCLEAR LEFT ALIGNMENT: {filepath}")
        
        # Ensure directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Name style (centered)
        name_style = ParagraphStyle(
            'Name',
            fontSize=18,
            spaceAfter=8,
            alignment=TA_CENTER,
            textColor=black,
            fontName='Times-Bold'
        )
        
        # Contact style (centered)
        contact_style = ParagraphStyle(
            'Contact',
            fontSize=11,
            spaceAfter=16,
            alignment=TA_CENTER,
            textColor=Color(0.2, 0.2, 0.2)
        )
        
        # Section header style (left, green)
        header_style = ParagraphStyle(
            'Header',
            fontSize=12,
            spaceAfter=8,
            spaceBefore=16,
            textColor=Color(0.18, 0.53, 0.35),  # Green
            fontName='Times-Bold',
            alignment=TA_LEFT
        )
        
        # NUCLEAR LEFT STYLE - FORCE EVERYTHING LEFT
        nuclear_left_style = ParagraphStyle(
            'NuclearLeft',
            fontSize=11,
            spaceAfter=2,
            spaceBefore=2,
            textColor=Color(0.1, 0.1, 0.1),
            alignment=TA_LEFT,
            leftIndent=0,
            rightIndent=0,
            fontName='Times-Roman'
        )
        
        # Build content
        story = []
        lines = resume_text.split('\n')
        
        section_headers = [
            'professional summary', 'summary', 'objective',
            'skills', 'technical skills', 'core competencies',
            'education', 'academic background',
            'experience', 'professional experience', 'work experience',
            'projects', 'key projects', 'notable projects',
            'certifications', 'certificates', 'awards',
            'achievements', 'accomplishments', 'languages',
            'volunteer', 'volunteer work', 'volunteering',
            'publications', 'research', 'papers',
            'hobbies', 'interests', 'activities',
            'memberships', 'professional memberships',
            'leadership', 'honors', 'recognition'
        ]
        
        logger.info(f"Processing {len(lines)} lines for PDF")
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            if not line_stripped:
                story.append(Spacer(1, 6))
                continue
            
            # Skip horizontal lines
            if line_stripped.startswith('-') and len(set(line_stripped)) <= 2:
                continue
            
            # First line is name (CENTERED)
            if i == 0 and not ('|' in line_stripped or '@' in line_stripped):
                story.append(Paragraph(line, name_style))
                logger.info(f"✅ NAME (centered): {line[:30]}")
                
            # Contact info (CENTERED) - but NOT if it contains University/College/dates/job titles
            elif ('|' in line_stripped or '@' in line_stripped or any(c.isdigit() for c in line_stripped)) and not any(inst in line_stripped for inst in ['University', 'College', 'Institute', 'School', 'GPA', 'Bachelor', 'Master', 'Degree', 'Engineering', 'Science', 'Technology', 'Arts', 'Commerce', 'Management', 'Intermediate', 'Junior', 'Senior', 'Intern', 'Developer', 'Engineer', 'Manager', 'Analyst', 'Consultant', 'Specialist', 'Coordinator', 'Assistant', 'Associate', 'Director', 'Lead', 'Principal', 'Staff', '2020', '2021', '2022', '2023', '2024', '2025', '2026']) and i <= 2:
                story.append(Paragraph(line, contact_style))
                logger.info(f"✅ CONTACT (centered): {line[:30]}")
                
            # Section headers (LEFT + GREEN UNDERLINE) - must be exact match or start of line
            elif (line_stripped.lower() in section_headers or 
                  any(line_stripped.lower().startswith(header) and len(line_stripped.split()) <= 3 for header in section_headers) or
                  (line_stripped.isupper() and len(line_stripped.split()) <= 3 and len(line_stripped) < 30 and line_stripped.isalpha())):
                # Add the section header with green text
                story.append(Paragraph(line, header_style))
                
                # Add green underline using Table
                underline_table = Table([['']],
                                      colWidths=[6*inch],
                                      rowHeights=[0.02*inch])
                underline_table.setStyle(TableStyle([
                    ('LINEBELOW', (0, 0), (0, 0), 0.5, Color(0.18, 0.53, 0.35)),  # Green underline
                    ('VALIGN', (0, 0), (0, 0), 'TOP'),
                ]))
                story.append(underline_table)
                story.append(Spacer(1, 4))  # Space after underline
                logger.info(f"✅ SECTION (left + underline): {line[:30]}")
                
            # ALL OTHER CONTENT - NUCLEAR LEFT ALIGNMENT (including education)
            else:
                story.append(Paragraph(line, nuclear_left_style))
                logger.info(f"🎯 FORCED LEFT: {line[:50]}")
        
        # Build the PDF
        doc.build(story)
        logger.info(f"✅ PDF created successfully with NUCLEAR LEFT alignment: {filepath}")
        
        # Verify file
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            logger.info(f"✅ PDF file verified: {os.path.getsize(filepath)} bytes")
            return True
        else:
            raise Exception("PDF file was not created properly")
        
    except Exception as e:
        logger.error(f"❌ Error creating PDF: {e}")
        return False


if __name__ == "__main__":
    # Test the function
    test_text = """John Doe
john@example.com | 555-123-4567

Professional Summary
Experienced software developer with 5 years of experience.

Education
Bachelor of Technology in Computer Science and Engineering
Anurag University | GPA: 7/10 | 2022-2026

Intermediate in MPC
XYZ Junior College | GPA: 8.4 | 2020-2022
"""
    
    create_simple_pdf(test_text, "test_resume.pdf")
    print("Test PDF created!")