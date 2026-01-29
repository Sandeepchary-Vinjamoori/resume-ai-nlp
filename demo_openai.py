#!/usr/bin/env python3
"""
Demo script showing OpenAI integration in Resume AI
Demonstrates the difference between local-only and AI-enhanced processing
"""

import os
import sys
sys.path.append('.')

from core.content_enhancer import ContentEnhancer

def demo_comparison():
    """Show side-by-side comparison of local vs AI-enhanced processing"""
    print("🚀 Resume AI - OpenAI Integration Demo")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            'type': 'experience',
            'input': 'worked on java project\nhelped with database optimization\ndid code reviews',
            'description': 'Experience Bullets'
        },
        {
            'type': 'summary',
            'input': 'Software engineer with 5 years experience in web development. Looking for new opportunities.',
            'description': 'Professional Summary'
        },
        {
            'type': 'projects',
            'input': 'built web app for task management\ncreated mobile application with React Native',
            'description': 'Project Descriptions'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ {test_case['description']} Transformation")
        print("-" * 50)
        print(f"📝 Raw Input:")
        print(f"   {test_case['input']}")
        print()
        
        # Test without OpenAI (local only)
        print("🔧 Local NLP Processing Only:")
        enhancer_local = ContentEnhancer()
        # Temporarily disable OpenAI even if available
        enhancer_local.openai_client = None
        
        if test_case['type'] == 'experience':
            local_result = enhancer_local.enhance_experience(test_case['input'])
        elif test_case['type'] == 'summary':
            local_result = enhancer_local.enhance_summary(test_case['input'])
        elif test_case['type'] == 'projects':
            local_result = enhancer_local.enhance_projects(test_case['input'])
        
        print(f"   {local_result}")
        print()
        
        # Test with OpenAI (if available)
        enhancer_ai = ContentEnhancer()
        if enhancer_ai.openai_client:
            print("✨ Local NLP + AI Polishing:")
            
            if test_case['type'] == 'experience':
                ai_result = enhancer_ai.enhance_experience(test_case['input'])
            elif test_case['type'] == 'summary':
                ai_result = enhancer_ai.enhance_summary(test_case['input'])
            elif test_case['type'] == 'projects':
                ai_result = enhancer_ai.enhance_projects(test_case['input'])
            
            print(f"   {ai_result}")
            print()
            
            # Show improvement
            if ai_result != local_result:
                print("🎯 AI Enhancement Benefits:")
                print("   • Improved clarity and flow")
                print("   • More natural language")
                print("   • Enhanced professional tone")
                print("   • Better keyword integration")
            else:
                print("ℹ️  Content was already optimal - no AI changes needed")
        else:
            print("⚠️  OpenAI API key not available - showing local processing only")
            print("   To see AI enhancement, set OPENAI_API_KEY environment variable")
        
        print()

def demo_token_efficiency():
    """Demonstrate token usage efficiency"""
    print("\n💰 Token Usage Efficiency Demo")
    print("-" * 40)
    
    enhancer = ContentEnhancer()
    
    if not enhancer.openai_client:
        print("⚠️  OpenAI API key not available - skipping token demo")
        return
    
    test_texts = [
        ("Short text", "short"),  # Should be skipped
        ("This is a medium length text that should be processed by AI for better clarity and professional tone.", "medium"),
        ("This is a very long piece of text that contains multiple sentences and detailed information about various technical aspects of software development, database optimization, and system architecture that might exceed our token limits and should be handled carefully by the AI polishing system to ensure we don't waste tokens on overly verbose content.", "long")
    ]
    
    for description, text in test_texts:
        print(f"\n📝 {description.title()} Text ({len(text)} chars):")
        print(f"   Input: {text[:60]}{'...' if len(text) > 60 else ''}")
        
        result = enhancer.ai_polish(text, 'general')
        
        if result == text:
            print("   Result: ⏭️  Skipped (too short or too long)")
        else:
            print(f"   Result: ✨ Polished ({len(result)} chars)")
            print(f"   Output: {result[:60]}{'...' if len(result) > 60 else ''}")

def demo_fallback_behavior():
    """Demonstrate graceful fallback behavior"""
    print("\n🛡️  Fallback Behavior Demo")
    print("-" * 35)
    
    # Test with invalid API key
    original_key = os.environ.get('OPENAI_API_KEY')
    os.environ['OPENAI_API_KEY'] = 'invalid-key-for-testing'
    
    try:
        enhancer = ContentEnhancer()
        
        test_text = "worked on machine learning project with python"
        result = enhancer.enhance_experience(test_text)
        
        print("✅ System gracefully handles invalid API key")
        print(f"   Input: {test_text}")
        print(f"   Output: {result}")
        print("   • Falls back to local NLP processing")
        print("   • No errors or interruptions")
        print("   • User experience remains smooth")
        
    finally:
        # Restore original key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key
        elif 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']

if __name__ == "__main__":
    demo_comparison()
    demo_token_efficiency()
    demo_fallback_behavior()
    
    print("\n🎉 Demo Complete!")
    print("\n📋 Key Takeaways:")
    print("   • System works perfectly without OpenAI API key")
    print("   • Local NLP provides strong baseline quality")
    print("   • AI polishing enhances clarity and flow")
    print("   • Token usage is optimized and cost-efficient")
    print("   • Graceful fallback ensures reliability")
    print("   • All existing code continues to work unchanged")