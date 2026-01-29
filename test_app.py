"""
Simple test script to verify the resume generation works
"""

def test_basic_resume_generation():
    """Test basic resume generation with minimal data"""
    
    # Import the generate_resume function
    from core.simple_builder import generate_resume
    
    # Create test data
    test_data = {
        "name": "John Doe",
        "email": "john.doe@example.com", 
        "phone": "+1 (555) 123-4567",
        "location": "San Francisco, CA",
        "objective": "Experienced software engineer seeking new opportunities",
        "skills": "Python, JavaScript, React, Node.js, SQL",
        "experience": "Software Engineer at Tech Company (2020-2023)\nDeveloped web applications\nImproved system performance",
        "education": "Bachelor of Science in Computer Science from University (2020)",
        "projects": "E-commerce Platform - Built using React and Node.js",
        "custom_sections": [
            {
                "title": "Certifications",
                "content": "AWS Certified Developer\nGoogle Cloud Professional"
            }
        ]
    }
    
    print("Testing resume generation...")
    
    try:
        # Generate resume
        resume_text = generate_resume(test_data, "modern")
        
        if resume_text and len(resume_text.strip()) > 100:
            print("✅ Resume generation successful!")
            print(f"Generated resume length: {len(resume_text)} characters")
            print("\nFirst 200 characters:")
            print(resume_text[:200] + "...")
            return True
        else:
            print("❌ Resume generation failed - empty or too short output")
            print(f"Output: {resume_text}")
            return False
            
    except Exception as e:
        print(f"❌ Resume generation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_functionality():
    """Test the export functionality"""
    
    from core.simple_exporter import export_to_docx
    import os
    
    test_resume_text = """JOHN DOE
========

Email: john.doe@example.com | Phone: +1 (555) 123-4567

PROFESSIONAL SUMMARY
------------------------------
Experienced software engineer seeking new opportunities

TECHNICAL SKILLS  
------------------------------
• Python
• JavaScript
• React
• Node.js
• SQL

PROFESSIONAL EXPERIENCE
------------------------------
• Software Engineer at Tech Company (2020-2023): Developed web applications
• Improved system performance

EDUCATION
------------------------------
Bachelor of Science in Computer Science from University (2020)

PROJECTS
------------------------------
• E-commerce Platform - Built using React and Node.js
"""
    
    print("\nTesting export functionality...")
    
    try:
        test_file = "test_resume.docx"
        export_to_docx(test_resume_text, test_file)
        
        if os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            print(f"✅ Export successful! File size: {file_size} bytes")
            
            # Clean up
            os.remove(test_file)
            return True
        else:
            print("❌ Export failed - file not created")
            return False
            
    except Exception as e:
        print(f"❌ Export failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Running Resume AI Tests\n")
    
    # Test 1: Basic resume generation
    test1_passed = test_basic_resume_generation()
    
    # Test 2: Export functionality  
    test2_passed = test_export_functionality()
    
    # Summary
    print(f"\n📊 Test Results:")
    print(f"Resume Generation: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Export Functionality: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The system is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")