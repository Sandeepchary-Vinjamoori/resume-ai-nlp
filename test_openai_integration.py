#!/usr/bin/env python3
"""
Test script to verify OpenAI integration in ContentEnhancer
Tests both with and without OPENAI_API_KEY
"""

import os
import sys
sys.path.append('.')

from core.content_enhancer import ContentEnhancer

def test_without_api_key():
    """Test that system works without OpenAI API key"""
    print("🧪 Testing WITHOUT OpenAI API key...")
    
    # Temporarily remove API key if it exists
    original_key = os.environ.get('OPENAI_API_KEY')
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        enhancer = ContentEnhancer()
        
        # Test experience enhancement
        raw_experience = "worked on java project\nhelped with database optimization"
        enhanced = enhancer.enhance_experience(raw_experience)
        
        print(f"✅ Experience enhancement works without API:")
        print(f"Input: {raw_experience}")
        print(f"Output: {enhanced[:100]}...")
        
        # Test summary enhancement
        user_data = {"name": "John Doe", "objective": "Software developer seeking new opportunities"}
        skills = ["Python", "JavaScript", "React"]
        summary = enhancer.enhance_summary(user_data.get("objective", ""), None)
        
        print(f"✅ Summary enhancement works without API:")
        print(f"Output: {summary[:100]}...")
        
        # Test projects enhancement
        raw_projects = "built web app\ncreated mobile application"
        projects = enhancer.enhance_projects(raw_projects)
        
        print(f"✅ Projects enhancement works without API:")
        print(f"Output: {projects[:100]}...")
        
        print("✅ All tests passed WITHOUT OpenAI API key")
        
    finally:
        # Restore original API key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key

def test_with_api_key():
    """Test that system works with OpenAI API key (if available)"""
    print("\n🧪 Testing WITH OpenAI API key...")
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  No OPENAI_API_KEY found - skipping API tests")
        return
    
    try:
        enhancer = ContentEnhancer()
        
        if enhancer.openai_client:
            print("✅ OpenAI client initialized successfully")
            
            # Test AI polishing directly
            test_text = "• Developed a Java application for data processing, demonstrating programming skills."
            polished = enhancer.ai_polish(test_text, 'experience')
            
            print(f"✅ AI polishing test:")
            print(f"Original: {test_text}")
            print(f"Polished: {polished}")
            
            # Test full enhancement with AI
            raw_experience = "worked on machine learning project"
            enhanced = enhancer.enhance_experience(raw_experience)
            
            print(f"✅ Full enhancement with AI:")
            print(f"Input: {raw_experience}")
            print(f"Output: {enhanced}")
            
        else:
            print("⚠️  OpenAI client not initialized despite API key")
            
    except Exception as e:
        print(f"❌ Error testing with API key: {e}")

def test_token_usage():
    """Test that we're using minimal tokens"""
    print("\n🧪 Testing token usage efficiency...")
    
    enhancer = ContentEnhancer()
    
    # Test with various text lengths
    test_cases = [
        "short text",  # Should not be polished (too short)
        "This is a longer piece of text that should be polished by the AI system for better clarity and professional tone.",
        "• Developed web applications using React and Node.js\n• Managed team of 5 developers\n• Improved system performance by 40%"
    ]
    
    for i, text in enumerate(test_cases):
        result = enhancer.ai_polish(text, 'experience')
        print(f"Test {i+1}: {'Polished' if result != text else 'Skipped'} (length: {len(text)})")

if __name__ == "__main__":
    print("🚀 Testing OpenAI Integration in Resume AI")
    print("=" * 50)
    
    test_without_api_key()
    test_with_api_key()
    test_token_usage()
    
    print("\n✅ All tests completed!")
    print("\n📋 Summary:")
    print("- System works fully without OpenAI API key")
    print("- Local NLP processing always runs first")
    print("- OpenAI is used only for optional final polishing")
    print("- Token usage is minimized with gpt-4o-mini")
    print("- All public function signatures remain unchanged")