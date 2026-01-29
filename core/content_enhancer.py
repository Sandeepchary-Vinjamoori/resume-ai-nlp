"""
Production-Grade Content Enhancer for ATS-Optimized Resume Generation

ARCHITECTURE:
- True linguistic processing using NLP analysis
- Action-oriented bullet point transformation
- Professional summary generation
- Keyword optimization for ATS systems
- Recruiter-grade content quality

FEATURES:
- Strong action verb enforcement
- Active voice transformation
- Quantified achievement extraction
- Weak verb elimination
- Professional tone optimization
- ATS keyword integration
"""

from typing import List, Dict, Any, Tuple, Optional
import re
import os
import logging
from .nlp_engine import NLPEngine

logger = logging.getLogger(__name__)

# Optional OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.info("OpenAI library not available - using local processing only")


class ContentEnhancer:
    def __init__(self):
        """Initialize the content enhancer with NLP engine and optional OpenAI client"""
        try:
            self.nlp_engine = NLPEngine()
            logger.info("NLP engine initialized successfully")
        except Exception as e:
            logger.warning(f"NLP engine initialization failed: {e}, using basic processing")
            self.nlp_engine = None
        
        # Initialize OpenAI client if API key is available
        self.openai_client = None
        if OPENAI_AVAILABLE and os.environ.get('OPENAI_API_KEY'):
            try:
                self.openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.warning(f"OpenAI client initialization failed: {e}")
                self.openai_client = None
        elif not OPENAI_AVAILABLE:
            logger.info("OpenAI library not available - using local processing only")
        else:
            logger.info("No OPENAI_API_KEY found - using local processing only")
        
        # Verb transformation mapping for professional language
        self.verb_transformations = {
            'worked': 'Developed',
            'helped': 'Implemented', 
            'did': 'Executed',
            'made': 'Built',
            'was responsible for': 'Managed',
            'handled': 'Managed',
            'dealt with': 'Resolved',
            'took care of': 'Maintained',
            'was involved in': 'Participated in',
            'used': 'Utilized',
            'got': 'Achieved',
            'tried': 'Implemented',
            'looked at': 'Analyzed',
            'worked on': 'Developed',
            'worked with': 'Collaborated with',
            'assisted': 'Supported',
            'participated': 'Contributed to',
            'contributed': 'Enhanced',
            'supported': 'Facilitated'
        }
        
        # Role-specific summary templates
        self.summary_templates = {
            'software': {
                'intro': 'Results-driven software engineer with {years} years of experience in {skills}.',
                'focus': 'Proven expertise in {domain} with a track record of {achievements}.',
                'goal': 'Seeking to leverage technical skills and leadership experience to drive innovation at a forward-thinking technology company.'
            },
            'data': {
                'intro': 'Analytical data professional with {years} years of experience in {skills}.',
                'focus': 'Specialized in {domain} with demonstrated success in {achievements}.',
                'goal': 'Looking to apply data-driven insights and analytical expertise to solve complex business challenges.'
            },
            'business': {
                'intro': 'Strategic business professional with {years} years of experience in {skills}.',
                'focus': 'Expert in {domain} with a proven ability to {achievements}.',
                'goal': 'Committed to driving organizational growth and operational excellence through strategic leadership.'
            }
        }

    def enhance_experience(self, raw_experience: str, analysis: Dict = None) -> str:
        """
        Transform raw experience into ATS-optimized bullet points
        
        Each bullet must:
        - Start with a strong action verb
        - Be in active voice
        - Contain one clear achievement
        - Be concise (1 line each)
        - Remove weak verbs
        """
        if not raw_experience or not raw_experience.strip():
            return ""
        
        # Analyze the text using NLP
        if self.nlp_engine:
            analysis = self.nlp_engine.analyze_text(raw_experience)
        else:
            analysis = {"sentences": [raw_experience], "verbs": [], "keywords": []}
        
        bullets = []
        sentences = analysis.get("sentences", [raw_experience])
        
        for sentence in sentences:
            if not sentence.strip():
                continue
                
            # Transform each sentence into a professional bullet
            enhanced_bullet = self._transform_to_bullet(sentence, analysis)
            if enhanced_bullet:
                bullets.append(enhanced_bullet)
        
        # If no bullets were created, create from raw text
        if not bullets:
            bullets = self._create_bullets_from_raw(raw_experience)
        
        result = '\n'.join(bullets)
        
        # Apply AI polishing if available
        if self.openai_client and result:
            result = self.ai_polish(result, 'experience')
        
        return result
    
    def _transform_to_bullet(self, sentence: str, analysis: Dict) -> str:
        """Transform a sentence into a professional bullet point"""
        sentence = sentence.strip()
        if not sentence:
            return ""
        
        # Remove bullet markers if present
        sentence = re.sub(r'^[•\-\*]\s*', '', sentence)
        
        # Replace weak verbs with strong ones
        for weak, strong in self.verb_transformations.items():
            pattern = r'\b' + re.escape(weak) + r'\b'
            sentence = re.sub(pattern, strong, sentence, flags=re.IGNORECASE)
        
        # Ensure it starts with a strong action verb
        sentence = self._ensure_strong_start(sentence)
        
        # Make it active voice
        sentence = self._convert_to_active_voice(sentence)
        
        # Add quantification if missing
        sentence = self._add_quantification(sentence, analysis)
        
        # Ensure proper capitalization and punctuation
        sentence = sentence.strip()
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
            if not sentence.endswith('.'):
                sentence += '.'
        
        return sentence
    
    def _ensure_strong_start(self, sentence: str) -> str:
        """Ensure sentence starts with a strong action verb"""
        if not sentence:
            return sentence
        
        # List of strong action verbs to use
        strong_verbs = [
            'Developed', 'Built', 'Created', 'Designed', 'Implemented', 'Engineered',
            'Led', 'Managed', 'Directed', 'Coordinated', 'Supervised', 'Mentored',
            'Optimized', 'Enhanced', 'Improved', 'Streamlined', 'Automated',
            'Achieved', 'Delivered', 'Executed', 'Completed', 'Launched',
            'Analyzed', 'Researched', 'Evaluated', 'Assessed', 'Investigated',
            'Collaborated', 'Partnered', 'Facilitated', 'Contributed', 'Supported'
        ]
        
        # Check if it already starts with a strong verb
        first_word = sentence.split()[0] if sentence.split() else ""
        if first_word.lower().rstrip('.,!?') in [v.lower() for v in strong_verbs]:
            return sentence
        
        # Try to identify the main action and replace with strong verb
        sentence_lower = sentence.lower()
        
        if any(word in sentence_lower for word in ['develop', 'build', 'creat']):
            return f"Developed {sentence}"
        elif any(word in sentence_lower for word in ['lead', 'manag', 'direct']):
            return f"Led {sentence}"
        elif any(word in sentence_lower for word in ['optim', 'improv', 'enhanc']):
            return f"Optimized {sentence}"
        elif any(word in sentence_lower for word in ['analyz', 'research', 'evaluat']):
            return f"Analyzed {sentence}"
        elif any(word in sentence_lower for word in ['collaborat', 'work with', 'partner']):
            return f"Collaborated on {sentence}"
        else:
            return f"Implemented {sentence}"
    
    def _convert_to_active_voice(self, sentence: str) -> str:
        """Convert passive voice to active voice"""
        # Common passive voice patterns
        passive_patterns = [
            (r'was (\w+ed)', r'\1'),
            (r'were (\w+ed)', r'\1'),
            (r'has been (\w+ed)', r'\1'),
            (r'have been (\w+ed)', r'\1'),
            (r'is (\w+ed)', r'\1'),
            (r'are (\w+ed)', r'\1')
        ]
        
        for pattern, replacement in passive_patterns:
            sentence = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
        
        return sentence
    
    def _add_quantification(self, sentence: str, analysis: Dict) -> str:
        """Add quantification to achievements if missing"""
        # Check if sentence already has quantification
        if re.search(r'\d+[%kmb]?|\$\d+|\d+x|\d+:\d+', sentence):
            return sentence
        
        # Extract quantified achievements from analysis
        if self.nlp_engine:
            achievements = self.nlp_engine.extract_quantified_achievements(sentence)
            if achievements:
                return sentence  # Already quantified
        
        # Add generic quantification based on context
        sentence_lower = sentence.lower()
        
        if 'performance' in sentence_lower or 'speed' in sentence_lower:
            if 'improv' in sentence_lower or 'optim' in sentence_lower:
                sentence = sentence.replace('.', ', improving performance by 25%.')
        elif 'cost' in sentence_lower or 'expense' in sentence_lower:
            if 'reduc' in sentence_lower or 'sav' in sentence_lower:
                sentence = sentence.replace('.', ', reducing costs by 20%.')
        elif 'time' in sentence_lower:
            if 'reduc' in sentence_lower or 'sav' in sentence_lower:
                sentence = sentence.replace('.', ', saving 15 hours per week.')
        elif 'user' in sentence_lower or 'customer' in sentence_lower:
            if 'improv' in sentence_lower or 'enhanc' in sentence_lower:
                sentence = sentence.replace('.', ', improving user satisfaction by 30%.')
        
        return sentence
    
    def _create_bullets_from_raw(self, raw_text: str) -> List[str]:
        """Create bullets from raw text when NLP analysis fails"""
        # Split by common delimiters
        sentences = re.split(r'[.!?;]\s*', raw_text)
        bullets = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short fragments
                bullet = self._transform_to_bullet(sentence, {})
                if bullet:
                    bullets.append(bullet)
        
        return bullets

    def enhance_summary(self, raw_summary: str, analysis: Dict = None) -> str:
        """
        Transform raw summary into professional 2-3 sentence summary
        
        Must be:
        - 2-3 sentences
        - Role-aware (software, data, business)
        - Keyword-rich but natural
        - Recruiter-written quality
        """
        if not raw_summary or not raw_summary.strip():
            return ""
        
        # Analyze the text
        if self.nlp_engine:
            analysis = self.nlp_engine.analyze_text(raw_summary)
        else:
            analysis = {"keywords": [], "tokens": []}
        
        # Detect role/domain
        domain = self._detect_domain(raw_summary, analysis)
        
        # Extract key information
        skills = self._extract_key_skills(raw_summary, analysis)
        years = self._extract_years_experience(raw_summary)
        achievements = self._extract_key_achievements(raw_summary)
        
        # Generate professional summary
        template = self.summary_templates.get(domain, self.summary_templates['software'])
        
        summary_parts = []
        
        # Intro sentence
        intro = template['intro'].format(
            years=years or "5+",
            skills=", ".join(skills[:3]) if skills else "full-stack development"
        )
        summary_parts.append(intro)
        
        # Focus sentence (if we have achievements)
        if achievements:
            focus = template['focus'].format(
                domain=domain.replace('_', ' '),
                achievements=achievements[0] if achievements else "delivering high-quality solutions"
            )
            summary_parts.append(focus)
        
        # Goal sentence
        summary_parts.append(template['goal'])
        
        result = " ".join(summary_parts)
        
        # Apply AI polishing if available
        if self.openai_client and result:
            result = self.ai_polish(result, 'summary')
        
        return result
    
    def _detect_domain(self, text: str, analysis: Dict) -> str:
        """Detect the professional domain from text"""
        text_lower = text.lower()
        keywords = analysis.get("keywords", [])
        
        # Software engineering indicators
        software_terms = ['software', 'developer', 'engineer', 'programming', 'code', 'api', 'web', 'app']
        if any(term in text_lower for term in software_terms):
            return 'software'
        
        # Data science indicators
        data_terms = ['data', 'analytics', 'machine learning', 'statistics', 'analysis', 'visualization']
        if any(term in text_lower for term in data_terms):
            return 'data'
        
        # Business indicators
        business_terms = ['business', 'management', 'strategy', 'operations', 'marketing', 'sales']
        if any(term in text_lower for term in business_terms):
            return 'business'
        
        return 'software'  # Default
    
    def _extract_key_skills(self, text: str, analysis: Dict) -> List[str]:
        """Extract key technical skills"""
        keywords = analysis.get("keywords", [])
        
        # Filter for technical skills
        technical_skills = []
        if self.nlp_engine:
            for keyword in keywords:
                if keyword in self.nlp_engine.skill_keywords:
                    technical_skills.append(keyword.title())
        
        # Fallback: extract from text directly
        if not technical_skills:
            text_lower = text.lower()
            common_skills = ['python', 'javascript', 'react', 'node.js', 'aws', 'docker', 'sql']
            for skill in common_skills:
                if skill in text_lower:
                    technical_skills.append(skill.title())
        
        return technical_skills[:5]  # Limit to top 5
    
    def _extract_years_experience(self, text: str) -> str:
        """Extract years of experience from text"""
        # Look for patterns like "5 years", "3+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?',
            r'over\s+(\d+)\s*years?',
            r'more than\s+(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                years = match.group(1)
                return f"{years}+"
        
        return None
    
    def _extract_key_achievements(self, text: str) -> List[str]:
        """Extract key achievements from summary"""
        if self.nlp_engine:
            return self.nlp_engine.extract_quantified_achievements(text)
        
        # Basic achievement extraction
        achievement_indicators = ['improved', 'increased', 'reduced', 'achieved', 'delivered', 'led']
        sentences = re.split(r'[.!?]', text)
        
        achievements = []
        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in achievement_indicators):
                achievements.append(sentence.strip())
        
        return achievements

    def enhance_skills(self, raw_skills: str, analysis: Dict = None) -> str:
        """
        Transform raw skills into categorized, keyword-rich format
        """
        if not raw_skills or not raw_skills.strip():
            return ""
        
        # Parse skills from text
        skills = self._parse_skills(raw_skills)
        
        # Categorize skills
        categorized = self._categorize_skills(skills)
        
        # Format for ATS optimization
        formatted_skills = []
        
        for category, skill_list in categorized.items():
            if skill_list:
                category_line = f"{category}: {', '.join(skill_list)}"
                formatted_skills.append(category_line)
        
        return '\n'.join(formatted_skills)
    
    def _parse_skills(self, raw_skills: str) -> List[str]:
        """Parse skills from raw text"""
        # Split by common delimiters
        skills = re.split(r'[,;|\n]', raw_skills)
        
        # Clean and filter skills
        cleaned_skills = []
        for skill in skills:
            skill = skill.strip()
            if skill and len(skill) > 1:
                cleaned_skills.append(skill)
        
        return cleaned_skills
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills for better ATS parsing"""
        categories = {
            "Programming Languages": [],
            "Frameworks & Libraries": [],
            "Databases": [],
            "Cloud & DevOps": [],
            "Tools & Platforms": []
        }
        
        # Categorization mappings
        programming_langs = ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'typescript']
        frameworks = ['react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'express']
        databases = ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle', 'sqlite']
        cloud_devops = ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform']
        tools = ['git', 'github', 'jira', 'postman', 'figma', 'photoshop']
        
        for skill in skills:
            skill_lower = skill.lower()
            
            if any(lang in skill_lower for lang in programming_langs):
                categories["Programming Languages"].append(skill)
            elif any(fw in skill_lower for fw in frameworks):
                categories["Frameworks & Libraries"].append(skill)
            elif any(db in skill_lower for db in databases):
                categories["Databases"].append(skill)
            elif any(cd in skill_lower for cd in cloud_devops):
                categories["Cloud & DevOps"].append(skill)
            elif any(tool in skill_lower for tool in tools):
                categories["Tools & Platforms"].append(skill)
            else:
                # Default to Tools & Platforms
                categories["Tools & Platforms"].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def enhance_education(self, raw_education: str, analysis: Dict = None) -> str:
        """Enhance education entries with proper formatting"""
        if not raw_education or not raw_education.strip():
            return ""
        
        # Clean up the education text
        education = raw_education.strip()
        
        # Ensure proper formatting
        if not education.startswith('•'):
            education = f"• {education}"
        
        return education

    def enhance_projects(self, raw_projects: str, analysis: Dict = None) -> str:
        """Transform project descriptions into professional format"""
        if not raw_projects or not raw_projects.strip():
            return ""
        
        # Analyze the text
        if self.nlp_engine:
            analysis = self.nlp_engine.analyze_text(raw_projects)
        else:
            analysis = {"sentences": [raw_projects]}
        
        # Transform each sentence
        sentences = analysis.get("sentences", [raw_projects])
        enhanced_sentences = []
        
        for sentence in sentences:
            if sentence.strip():
                enhanced = self._transform_to_bullet(sentence, analysis)
                if enhanced:
                    enhanced_sentences.append(enhanced)
        
        result = '\n'.join(enhanced_sentences)
        
        # Apply AI polishing if available
        if self.openai_client and result:
            result = self.ai_polish(result, 'projects')
        
        return result

    def enhance_custom_section(self, title: str, content: str, analysis: Dict = None) -> str:
        """Enhance custom section content"""
        if not content or not content.strip():
            return ""
        
        # For certifications, awards, etc., keep formatting simple but professional
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Ensure proper bullet formatting
                if not line.startswith('•'):
                    line = f"• {line}"
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)

    def ai_polish(self, text: str, content_type: str = 'general') -> str:
        """
        Polish text using OpenAI API for enhanced clarity and flow
        
        Args:
            text: The text to polish (already enhanced by local NLP)
            content_type: Type of content ('summary', 'experience', 'projects', 'general')
        
        Returns:
            Polished text or original text if API unavailable/fails
        """
        # Return original text if OpenAI not available
        if not self.openai_client:
            return text
        
        # Skip polishing for very short text (not worth the API call)
        if len(text.strip()) < 50:
            return text
        
        # Validate token count (rough estimate: 1 token ≈ 4 characters)
        estimated_tokens = len(text) // 4
        if estimated_tokens > 400:  # Leave room for response
            logger.warning(f"Text too long for polishing ({estimated_tokens} tokens), skipping AI polish")
            return text
        
        try:
            # Create content-specific prompts
            prompts = {
                'summary': "Polish this professional summary for clarity and impact. Keep it 2-3 sentences, maintain all technical details, and ensure it sounds natural and engaging:",
                'experience': "Polish these experience bullet points for clarity and professional tone. Maintain all technical details, metrics, and action verbs. Keep the bullet point format:",
                'projects': "Polish these project descriptions for clarity and impact. Maintain all technical details and keep the professional tone:",
                'general': "Polish this text for clarity and professional tone while maintaining all technical details:"
            }
            
            prompt = prompts.get(content_type, prompts['general'])
            
            # Make API call with minimal token usage
            response = self.openai_client.chat.completions.create(
                model=os.environ.get('OPENAI_MODEL', 'gpt-4o-mini'),
                messages=[
                    {"role": "system", "content": "You are a professional resume writer. Polish the provided text while maintaining all technical details, metrics, and professional formatting."},
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ],
                max_tokens=500,
                temperature=0.3  # Lower temperature for more consistent, professional output
            )
            
            polished_text = response.choices[0].message.content.strip()
            
            # Validate the response
            if polished_text and len(polished_text) > 10:
                logger.info(f"Successfully polished {content_type} content ({len(text)} -> {len(polished_text)} chars)")
                return polished_text
            else:
                logger.warning("AI polishing returned empty/invalid response, using original text")
                return text
                
        except Exception as e:
            logger.warning(f"AI polishing failed: {e}, using original text")
            return text

    def enhance_experience_with_ai(self, raw_experience: str, analysis: Dict = None) -> str:
        """Enhanced experience processing with optional AI polishing"""
        # First, apply local NLP enhancement
        enhanced_text = self.enhance_experience(raw_experience, analysis)
        
        # Then apply AI polishing if available
        if self.openai_client and enhanced_text:
            enhanced_text = self.ai_polish(enhanced_text, 'experience')
        
        return enhanced_text

    def enhance_summary_with_ai(self, raw_summary: str, analysis: Dict = None) -> str:
        """Enhanced summary processing with optional AI polishing"""
        # First, apply local NLP enhancement
        enhanced_text = self.enhance_summary(raw_summary, analysis)
        
        # Then apply AI polishing if available
        if self.openai_client and enhanced_text:
            enhanced_text = self.ai_polish(enhanced_text, 'summary')
        
        return enhanced_text

    def enhance_projects_with_ai(self, raw_projects: str, analysis: Dict = None) -> str:
        """Enhanced projects processing with optional AI polishing"""
        # First, apply local NLP enhancement
        enhanced_text = self.enhance_projects(raw_projects, analysis)
        
        # Then apply AI polishing if available
        if self.openai_client and enhanced_text:
            enhanced_text = self.ai_polish(enhanced_text, 'projects')
        
        return enhanced_text