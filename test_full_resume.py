#!/usr/bin/env python3
"""
Test script to verify complete resume generation with all sections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.simple_builder import generate_resume

def test_complete_resume():
    """Test resume generation with comprehensive data"""
    
    # Comprehensive test data
    test_data = {
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'phone': '+1 (555) 123-4567',
        'location': 'San Francisco, CA',
        'linkedin': 'linkedin.com/in/johndoe',
        'website': 'johndoe.dev',
        'objective': 'Experienced software engineer with 5+ years of experience in full-stack development, seeking to leverage expertise in Python, JavaScript, and cloud technologies to drive innovation at a forward-thinking tech company.',
        'skills': 'Programming Languages: Python, JavaScript, Java, C++\nFrameworks: React, Node.js, Django, Flask\nDatabases: PostgreSQL, MongoDB, Redis\nCloud: AWS, Docker, Kubernetes\nTools: Git, Jenkins, Terraform',
        
        # Education entries
        'education_entries': [
            {
                'institution': 'Stanford University',
                'degree': 'Master of Science',
                'field': 'Computer Science',
                'start': '2018',
                'end': '2020',
                'gpa': '3.8',
                'achievements': 'Thesis on Machine Learning Optimization, Dean\'s List, Teaching Assistant for Data Structures'
            },
            {
                'institution': 'UC Berkeley',
                'degree': 'Bachelor of Science',
                'field': 'Computer Engineering',
                'start': '2014',
                'end': '2018',
                'gpa': '3.6',
                'achievements': 'Summa Cum Laude, ACM Programming Contest Winner, Senior Design Project Award'
            }
        ],
        
        # Experience entries
        'experience_entries': [
            {
                'company': 'Google',
                'title': 'Senior Software Engineer',
                'start': 'Jan 2021',
                'end': 'Present',
                'responsibilities': 'Lead development of microservices architecture serving 10M+ users daily\nMentor junior developers and conduct technical interviews\nCollaborate with product managers to define technical requirements\nOptimize system performance and reduce latency by 40%',
                'achievements': 'Promoted to Senior Engineer within 18 months\nLed migration to Kubernetes, reducing infrastructure costs by 30%\nImplemented CI/CD pipeline improving deployment frequency by 5x\nReceived "Outstanding Contributor" award for Q3 2023'
            },
            {
                'company': 'Facebook (Meta)',
                'title': 'Software Engineer',
                'start': 'Jun 2020',
                'end': 'Dec 2020',
                'responsibilities': 'Developed React components for News Feed optimization\nImplemented A/B testing framework for feature rollouts\nWorked on backend APIs handling billions of requests\nParticipated in on-call rotation and incident response',
                'achievements': 'Improved News Feed engagement by 15% through algorithm optimization\nReduced API response time by 25% through caching strategies\nContributed to open-source React libraries used by 1M+ developers'
            },
            {
                'company': 'Startup Inc',
                'title': 'Full Stack Developer',
                'start': 'Aug 2018',
                'end': 'May 2020',
                'responsibilities': 'Built entire web application from scratch using MERN stack\nDesigned and implemented RESTful APIs and database schemas\nIntegrated third-party services including payment processing\nManaged AWS infrastructure and deployment pipelines',
                'achievements': 'Delivered MVP 2 weeks ahead of schedule\nScaled application to handle 100K+ concurrent users\nReduced server costs by 50% through optimization\nImplemented security measures achieving SOC 2 compliance'
            }
        ],
        
        # Project entries
        'project_entries': [
            {
                'name': 'AI-Powered Resume Builder',
                'description': 'Full-stack web application that uses natural language processing and machine learning to generate ATS-optimized resumes. Features include real-time preview, multiple export formats, and intelligent content suggestions.',
                'technologies': 'Python, Flask, React, OpenAI API, PostgreSQL, Docker, AWS',
                'link': 'https://github.com/johndoe/resume-ai'
            },
            {
                'name': 'Distributed Task Scheduler',
                'description': 'Microservices-based task scheduling system capable of handling millions of jobs with fault tolerance and horizontal scaling. Includes web dashboard for monitoring and management.',
                'technologies': 'Go, Redis, PostgreSQL, Kubernetes, Prometheus, Grafana',
                'link': 'https://github.com/johndoe/task-scheduler'
            },
            {
                'name': 'Real-time Chat Application',
                'description': 'Scalable chat application supporting group conversations, file sharing, and video calls. Built with modern web technologies and deployed on cloud infrastructure.',
                'technologies': 'Node.js, Socket.io, React, MongoDB, WebRTC, AWS',
                'link': 'https://github.com/johndoe/chat-app'
            }
        ],
        
        # Custom sections
        'custom_sections': [
            {
                'title': 'Certifications',
                'content': 'AWS Certified Solutions Architect - Professional (2023)\nGoogle Cloud Professional Developer (2022)\nCertified Kubernetes Administrator (CKA) (2021)\nMongoDB Certified Developer (2020)'
            },
            {
                'title': 'Publications & Speaking',
                'content': 'Published "Optimizing Microservices Performance" in IEEE Software Magazine (2023)\nKeynote speaker at DevOps Conference 2023: "Scaling Engineering Teams"\nTech talk at Google I/O 2022: "Building Resilient Distributed Systems"\nGuest lecturer at Stanford CS Department on "Modern Web Architecture"'
            },
            {
                'title': 'Awards & Recognition',
                'content': 'Google Peer Bonus Award for exceptional collaboration (2023)\nHackathon Winner - Best Technical Innovation at TechCrunch Disrupt (2022)\nOpen Source Contributor Award - React Community (2021)\nEmployee of the Month - Startup Inc (March 2019)'
            }
        ]
    }
    
    print("🧪 Testing complete resume generation...")
    print(f"📊 Test data summary:")
    print(f"   - Education entries: {len(test_data['education_entries'])}")
    print(f"   - Experience entries: {len(test_data['experience_entries'])}")
    print(f"   - Project entries: {len(test_data['project_entries'])}")
    print(f"   - Custom sections: {len(test_data['custom_sections'])}")
    print()
    
    # Generate resume
    resume_text = generate_resume(test_data, 'modern')
    
    print(f"✅ Resume generated successfully!")
    print(f"📄 Total length: {len(resume_text)} characters")
    print(f"📝 Total lines: {len(resume_text.split(chr(10)))}")
    print()
    
    # Check for all expected sections
    sections_to_check = [
        'PROFESSIONAL SUMMARY',
        'TECHNICAL SKILLS', 
        'EDUCATION',
        'PROFESSIONAL EXPERIENCE',
        'PROJECTS',
        'CERTIFICATIONS',
        'PUBLICATIONS',
        'AWARDS'
    ]
    
    print("🔍 Checking for expected sections:")
    for section in sections_to_check:
        if section in resume_text.upper():
            print(f"   ✅ {section}")
        else:
            print(f"   ❌ {section} - MISSING!")
    
    print()
    print("📋 Full resume content:")
    print("=" * 80)
    print(resume_text)
    print("=" * 80)
    
    # Check specific content
    print("\n🔍 Content verification:")
    if 'Google' in resume_text:
        print("   ✅ Google experience included")
    else:
        print("   ❌ Google experience missing")
        
    if 'Stanford' in resume_text:
        print("   ✅ Stanford education included")
    else:
        print("   ❌ Stanford education missing")
        
    if 'AI-Powered Resume Builder' in resume_text:
        print("   ✅ Projects included")
    else:
        print("   ❌ Projects missing")
        
    if 'AWS Certified' in resume_text:
        print("   ✅ Certifications included")
    else:
        print("   ❌ Certifications missing")
    
    return resume_text

if __name__ == "__main__":
    test_complete_resume()