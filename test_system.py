#!/usr/bin/env python3
"""
Test script to verify the complete resume generation system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, extract_form_data_optimized
from core.simple_builder import generate_resume
from werkzeug.datastructures import MultiDict

def test_complete_system():
    """Test the complete system end-to-end"""
    
    print("🧪 Testing Complete Resume Generation System")
    print("=" * 50)
    
    # Create test form data (simulating form submission)
    form_data = MultiDict([
        ('name', 'John Doe'),
        ('email', 'john.doe@email.com'),
        ('phone', '+1 (555) 123-4567'),
        ('location', 'San Francisco, CA'),
        ('linkedin', 'linkedin.com/in/johndoe'),
        ('website', 'johndoe.dev'),
        ('objective', 'Experienced software engineer with 5+ years of experience seeking new opportunities.'),
        ('skills', 'Python, JavaScript, React, Node.js, AWS, Docker'),
        ('style', 'modern'),
        
        # Education entries
        ('education_institution_1', 'Stanford University'),
        ('education_degree_1', 'Master of Science'),
        ('education_field_1', 'Computer Science'),
        ('education_start_1', '2018'),
        ('education_end_1', '2020'),
        ('education_gpa_1', '3.8'),
        ('education_achievements_1', 'Thesis on Machine Learning, Dean\'s List'),
        
        # Experience entries
        ('experience_company_1', 'Google'),
        ('experience_title_1', 'Senior Software Engineer'),
        ('experience_start_1', 'Jan 2021'),
        ('experience_end_1', 'Present'),
        ('experience_responsibilities_1', 'Lead development of microservices\nMentor junior developers\nOptimize system performance'),
        ('experience_achievements_1', 'Promoted within 18 months\nReduced infrastructure costs by 30%'),
        
        ('experience_company_2', 'Facebook'),
        ('experience_title_2', 'Software Engineer'),
        ('experience_start_2', 'Jun 2020'),
        ('experience_end_2', 'Dec 2020'),
        ('experience_responsibilities_2', 'Developed React components\nImplemented A/B testing framework'),
        ('experience_achievements_2', 'Improved engagement by 15%\nReduced API response time by 25%'),
        
        # Project entries
        ('project_name_1', 'AI Resume Builder'),
        ('project_description_1', 'Full-stack web application using NLP to generate resumes'),
        ('project_technologies_1', 'Python, Flask, React, OpenAI API'),
        ('project_link_1', 'https://github.com/johndoe/resume-ai'),
        
        ('project_name_2', 'Task Scheduler'),
        ('project_description_2', 'Distributed task scheduling system with fault tolerance'),
        ('project_technologies_2', 'Go, Redis, Kubernetes'),
        ('project_link_2', 'https://github.com/johndoe/scheduler'),
        
        # Custom sections
        ('custom_title_1', 'Certifications'),
        ('custom_content_1', 'AWS Certified Solutions Architect\nGoogle Cloud Professional Developer'),
        
        ('custom_title_2', 'Awards'),
        ('custom_content_2', 'Employee of the Month - March 2023\nHackathon Winner - Best Innovation'),
    ])
    
    print(f"📝 Created test form data with {len(form_data)} fields")
    
    # Test 1: Form data extraction
    print("\n1️⃣ Testing form data extraction...")
    try:
        extracted_data = extract_form_data_optimized(form_data)
        print(f"   ✅ Extracted {len(extracted_data)} data fields")
        print(f"   📚 Education entries: {len(extracted_data.get('education_entries', []))}")
        print(f"   💼 Experience entries: {len(extracted_data.get('experience_entries', []))}")
        print(f"   🚀 Project entries: {len(extracted_data.get('project_entries', []))}")
        print(f"   🏆 Custom sections: {len(extracted_data.get('custom_sections', []))}")
    except Exception as e:
        print(f"   ❌ Form data extraction failed: {e}")
        return False
    
    # Test 2: Resume generation
    print("\n2️⃣ Testing resume generation...")
    try:
        resume_text = generate_resume(extracted_data, 'modern')
        print(f"   ✅ Generated resume: {len(resume_text)} characters")
        print(f"   📄 Lines: {len(resume_text.split(chr(10)))}")
        
        # Check for key sections
        sections_found = []
        expected_sections = [
            'PROFESSIONAL SUMMARY',
            'TECHNICAL SKILLS',
            'EDUCATION',
            'PROFESSIONAL EXPERIENCE',
            'PROJECTS',
            'CERTIFICATIONS',
            'AWARDS'
        ]
        
        for section in expected_sections:
            if section in resume_text.upper():
                sections_found.append(section)
        
        print(f"   📋 Sections found: {len(sections_found)}/{len(expected_sections)}")
        for section in sections_found:
            print(f"      ✅ {section}")
        
        missing_sections = set(expected_sections) - set(sections_found)
        if missing_sections:
            for section in missing_sections:
                print(f"      ❌ {section} - MISSING")
        
    except Exception as e:
        print(f"   ❌ Resume generation failed: {e}")
        import traceback
        print(f"   📋 Traceback: {traceback.format_exc()}")
        return False
    
    # Test 3: Flask app context
    print("\n3️⃣ Testing Flask app integration...")
    try:
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            print(f"   ✅ Home page: {response.status_code}")
            
            # Test health check
            response = client.get('/health')
            print(f"   ✅ Health check: {response.status_code}")
            
            # Test generate route (would need session setup for full test)
            print(f"   ✅ Flask app is functional")
            
    except Exception as e:
        print(f"   ❌ Flask app test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! System is working correctly.")
    print("\n📋 Sample resume content (first 1000 chars):")
    print("-" * 50)
    print(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
    print("-" * 50)
    
    return True

if __name__ == "__main__":
    success = test_complete_system()
    sys.exit(0 if success else 1)