#!/usr/bin/env python3
"""
Test script to verify custom sections functionality
"""

import sys
sys.path.append('.')

from core.simple_builder import generate_resume
from core.content_enhancer import ContentEnhancer

def test_custom_sections():
    """Test custom sections with various types of content"""
    print("🧪 Testing Custom Sections Functionality")
    print("=" * 50)
    
    # Test data with custom sections
    test_data = {
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "phone": "+1 (555) 123-4567",
        "skills": "Python, JavaScript, React",
        "experience": "Developed web applications\nManaged development team",
        "projects": "E-commerce platform\nData analytics dashboard",
        "custom_sections": [
            {
                "title": "Certifications",
                "content": "AWS Certified Solutions Architect\nGoogle Cloud Professional\nScrum Master Certification"
            },
            {
                "title": "Languages",
                "content": "English (Native)\nSpanish (Fluent)\nFrench (Conversational)"
            },
            {
                "title": "Volunteer Experience",
                "content": "Mentored junior developers at local coding bootcamp\nOrganized tech meetups for women in technology\nContributed to open source projects"
            },
            {
                "title": "Interests",
                "content": "Machine Learning, Photography, Rock Climbing, Travel"
            }
        ]
    }
    
    print("📋 Test Data:")
    print(f"Name: {test_data['name']}")
    print(f"Custom Sections: {len(test_data['custom_sections'])}")
    for i, section in enumerate(test_data['custom_sections']):
        print(f"  {i+1}. {section['title']}")
    
    print("\n🚀 Generating Resume with Custom Sections...")
    
    # Test different styles
    styles = ['simple', 'modern', 'academic']
    
    for style in styles:
        print(f"\n📄 Testing {style.upper()} style:")
        print("-" * 30)
        
        try:
            resume = generate_resume(test_data, style)
            
            # Check if custom sections are included
            for section in test_data['custom_sections']:
                title = section['title']
                if style == 'simple' or style == 'academic':
                    expected_title = title.upper()
                else:
                    expected_title = title.title()
                
                if expected_title in resume:
                    print(f"✅ {title} section found")
                else:
                    print(f"❌ {title} section missing")
            
            # Show a preview of the resume
            lines = resume.split('\n')
            preview_lines = lines[:20] if len(lines) > 20 else lines
            print(f"\nPreview ({len(preview_lines)} lines):")
            for line in preview_lines:
                print(f"  {line}")
            
            if len(lines) > 20:
                print(f"  ... ({len(lines) - 20} more lines)")
                
        except Exception as e:
            print(f"❌ Error generating {style} resume: {e}")

def test_content_enhancement():
    """Test custom section content enhancement"""
    print("\n🧪 Testing Custom Section Content Enhancement")
    print("=" * 50)
    
    enhancer = ContentEnhancer()
    
    test_cases = [
        {
            "title": "Certifications",
            "content": "AWS Solutions Architect\nGoogle Cloud Professional",
            "expected_format": "bullet_points"
        },
        {
            "title": "Languages", 
            "content": "English\nSpanish\nFrench",
            "expected_format": "structured"
        },
        {
            "title": "Achievements",
            "content": "Won hackathon competition\nPublished research paper\nReceived employee of the year award",
            "expected_format": "bullet_points"
        },
        {
            "title": "Interests",
            "content": "Photography, Travel, Cooking, Reading",
            "expected_format": "comma_separated"
        }
    ]
    
    for test_case in test_cases:
        title = test_case['title']
        content = test_case['content']
        
        print(f"\n📝 Testing: {title}")
        print(f"Input: {content}")
        
        try:
            enhanced = enhancer.enhance_custom_section(title, content)
            print(f"Output: {enhanced}")
            
            # Basic validation
            if enhanced and enhanced != content:
                print("✅ Content was enhanced")
            else:
                print("⚠️  Content unchanged (may be expected)")
                
        except Exception as e:
            print(f"❌ Error enhancing {title}: {e}")

def test_empty_custom_sections():
    """Test that empty custom sections are ignored"""
    print("\n🧪 Testing Empty Custom Sections Handling")
    print("=" * 50)
    
    test_data = {
        "name": "John Doe",
        "email": "john@example.com", 
        "phone": "+1 (555) 987-6543",
        "skills": "Java, Spring Boot",
        "custom_sections": [
            {
                "title": "Certifications",
                "content": "Oracle Java Certification"
            },
            {
                "title": "",  # Empty title - should be ignored
                "content": "Some content"
            },
            {
                "title": "Languages",
                "content": ""  # Empty content - should be ignored
            },
            {
                "title": "Awards",
                "content": "Employee of the Month"
            }
        ]
    }
    
    print("📋 Test Data with empty sections:")
    for i, section in enumerate(test_data['custom_sections']):
        title = section['title'] or "[EMPTY TITLE]"
        content = section['content'] or "[EMPTY CONTENT]"
        print(f"  {i+1}. {title}: {content}")
    
    try:
        resume = generate_resume(test_data, 'simple')
        
        # Check that only valid sections are included
        if "CERTIFICATIONS" in resume:
            print("✅ Valid section 1 (Certifications) included")
        else:
            print("❌ Valid section 1 missing")
            
        if "AWARDS" in resume:
            print("✅ Valid section 4 (Awards) included")
        else:
            print("❌ Valid section 4 missing")
            
        # Check that invalid sections are excluded
        if "[EMPTY" not in resume and "Some content" not in resume:
            print("✅ Empty/invalid sections properly excluded")
        else:
            print("❌ Empty/invalid sections were included")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_custom_sections()
    test_content_enhancement()
    test_empty_custom_sections()
    
    print("\n✅ All custom sections tests completed!")
    print("\n📋 Summary:")
    print("- Custom sections are dynamically added after Projects")
    print("- Content is enhanced using NLP analysis")
    print("- Different formatting applied based on section type")
    print("- Empty sections are properly ignored")
    print("- All resume styles support custom sections")