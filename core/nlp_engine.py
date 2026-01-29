"""
Advanced NLP Engine for Resume AI using spaCy
True linguistic processing for ATS-optimized resume generation

FEATURES:
- Advanced tokenization and POS tagging
- Action verb extraction and enhancement
- Skill entity recognition
- Domain keyword extraction
- ATS-friendly content analysis
- Quantified impact detection
"""

from typing import List, Dict, Any, Set, Tuple
from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)


class NLPEngine:
    def __init__(self):
        """Initialize the NLP engine with spaCy model and ATS optimization rules"""
        self.nlp = None
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy English model loaded successfully")
        except (OSError, ImportError) as e:
            logger.warning(f"spaCy not available: {e}. Using basic text processing.")
        
        # Comprehensive technical skills database for ATS optimization
        self.skill_keywords = {
            # Programming Languages
            'python', 'javascript', 'java', 'typescript', 'c++', 'c#', 'php', 'ruby',
            'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl', 'shell',
            
            # Web Technologies
            'html', 'css', 'react', 'angular', 'vue.js', 'node.js', 'express',
            'django', 'flask', 'spring', 'laravel', 'rails', 'asp.net', 'jquery',
            'bootstrap', 'tailwind', 'sass', 'webpack', 'babel', 'npm', 'yarn',
            
            # Databases
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'sqlite', 'cassandra', 'dynamodb', 'neo4j', 'influxdb',
            
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab',
            'terraform', 'ansible', 'chef', 'puppet', 'vagrant', 'nginx', 'apache',
            
            # Data Science & ML
            'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'keras',
            'matplotlib', 'seaborn', 'jupyter', 'spark', 'hadoop', 'tableau',
            
            # Tools & Platforms
            'git', 'github', 'bitbucket', 'jira', 'confluence', 'slack', 'trello',
            'postman', 'swagger', 'figma', 'sketch', 'photoshop', 'illustrator'
        }
        
        # Strong action verbs for resume optimization
        self.strong_action_verbs = {
            'leadership': [
                'led', 'managed', 'directed', 'supervised', 'coordinated', 'guided',
                'mentored', 'coached', 'facilitated', 'orchestrated', 'spearheaded',
                'championed', 'drove', 'initiated', 'established', 'founded'
            ],
            'development': [
                'developed', 'built', 'created', 'designed', 'implemented', 'engineered',
                'architected', 'programmed', 'coded', 'constructed', 'launched',
                'deployed', 'delivered', 'produced', 'generated', 'crafted'
            ],
            'improvement': [
                'optimized', 'enhanced', 'improved', 'streamlined', 'upgraded',
                'modernized', 'refactored', 'automated', 'accelerated', 'strengthened',
                'transformed', 'revolutionized', 'innovated', 'advanced', 'refined'
            ],
            'achievement': [
                'achieved', 'accomplished', 'delivered', 'exceeded', 'surpassed',
                'completed', 'executed', 'realized', 'attained', 'secured',
                'earned', 'won', 'gained', 'obtained', 'reached'
            ],
            'analysis': [
                'analyzed', 'evaluated', 'assessed', 'investigated', 'researched',
                'examined', 'studied', 'reviewed', 'audited', 'diagnosed',
                'identified', 'discovered', 'uncovered', 'determined', 'measured'
            ],
            'collaboration': [
                'collaborated', 'partnered', 'cooperated', 'contributed', 'participated',
                'engaged', 'liaised', 'communicated', 'interfaced', 'coordinated',
                'synchronized', 'aligned', 'unified', 'integrated', 'facilitated'
            ]
        }
        
        # Weak verbs to replace
        self.weak_verbs = {
            'worked': 'developed',
            'helped': 'implemented', 
            'did': 'executed',
            'made': 'built',
            'was responsible for': 'managed',
            'handled': 'managed',
            'dealt with': 'resolved',
            'took care of': 'maintained',
            'was involved in': 'participated in',
            'used': 'utilized',
            'got': 'achieved',
            'tried': 'attempted',
            'looked at': 'analyzed',
            'worked on': 'developed',
            'worked with': 'collaborated with'
        }
        
        # Stop words to remove during analysis
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'i', 'my', 'me', 'we', 'our', 'us'
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Perform comprehensive NLP analysis on text
        
        Returns:
            Dict with tokens, keywords, verbs, and sentences
        """
        if not text or not text.strip():
            return {
                "tokens": [],
                "keywords": [],
                "verbs": [],
                "sentences": []
            }
        
        if self.nlp:
            return self._analyze_with_spacy(text)
        else:
            return self._analyze_basic(text)
    
    def _analyze_with_spacy(self, text: str) -> Dict[str, Any]:
        """Advanced analysis using spaCy"""
        doc = self.nlp(text)
        
        # Extract tokens (lemmatized, no stopwords)
        tokens = []
        for token in doc:
            if (not token.is_stop and 
                not token.is_punct and 
                not token.is_space and
                len(token.text) > 2 and
                token.lemma_.lower() not in self.stop_words):
                tokens.append(token.lemma_.lower())
        
        # Extract keywords (noun phrases + domain terms)
        keywords = []
        
        # Get noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text) > 2:
                keywords.append(chunk.text.lower())
        
        # Add technical skills found in text
        text_lower = text.lower()
        for skill in self.skill_keywords:
            if skill in text_lower:
                keywords.append(skill)
        
        # Extract action verbs
        verbs = []
        for token in doc:
            if token.pos_ == "VERB":
                lemma = token.lemma_.lower()
                # Check if it's a strong action verb
                for category, verb_list in self.strong_action_verbs.items():
                    if lemma in verb_list:
                        verbs.append(lemma)
                        break
        
        # Extract and clean sentences
        sentences = []
        for sent in doc.sents:
            clean_sent = sent.text.strip()
            if len(clean_sent) > 10:  # Filter out very short sentences
                sentences.append(clean_sent)
        
        return {
            "tokens": list(set(tokens)),
            "keywords": list(set(keywords)),
            "verbs": list(set(verbs)),
            "sentences": sentences
        }
    
    def _analyze_basic(self, text: str) -> Dict[str, Any]:
        """Basic analysis without spaCy"""
        # Basic tokenization
        words = re.findall(r'\b\w+\b', text.lower())
        tokens = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        # Extract keywords (technical skills)
        keywords = []
        text_lower = text.lower()
        for skill in self.skill_keywords:
            if skill in text_lower:
                keywords.append(skill)
        
        # Extract verbs (basic pattern matching)
        verbs = []
        for word in words:
            for category, verb_list in self.strong_action_verbs.items():
                if word in verb_list:
                    verbs.append(word)
                    break
        
        # Extract sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if len(s.strip()) > 10]
        
        return {
            "tokens": list(set(tokens)),
            "keywords": list(set(keywords)),
            "verbs": list(set(verbs)),
            "sentences": sentences
        }
    
    def extract_quantified_achievements(self, text: str) -> List[str]:
        """Extract quantified achievements from text"""
        # Patterns for numbers and percentages
        number_patterns = [
            r'\d+%',  # percentages
            r'\d+\+',  # numbers with plus
            r'\$\d+[kmb]?',  # dollar amounts
            r'\d+[kmb]',  # numbers with k/m/b suffix
            r'\d+x',  # multipliers
            r'\d+:\d+',  # ratios
            r'\d+\.\d+',  # decimals
            r'\d{1,3}(?:,\d{3})*',  # large numbers with commas
        ]
        
        achievements = []
        for pattern in number_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                achievements.append(context)
        
        return achievements
    
    def get_strong_verb_replacement(self, weak_verb: str) -> str:
        """Get strong verb replacement for weak verb"""
        weak_verb_lower = weak_verb.lower()
        
        # Direct mapping
        if weak_verb_lower in self.weak_verbs:
            return self.weak_verbs[weak_verb_lower]
        
        # Pattern matching for common weak patterns
        if 'work' in weak_verb_lower:
            return 'developed'
        elif 'help' in weak_verb_lower:
            return 'implemented'
        elif 'do' in weak_verb_lower or 'did' in weak_verb_lower:
            return 'executed'
        elif 'make' in weak_verb_lower or 'made' in weak_verb_lower:
            return 'built'
        
        return weak_verb  # Return original if no replacement found
    
    def extract_domain_keywords(self, text: str, domain: str = 'software') -> List[str]:
        """Extract domain-specific keywords"""
        domain_keywords = {
            'software': [
                'agile', 'scrum', 'api', 'microservices', 'architecture', 'scalable',
                'performance', 'optimization', 'testing', 'debugging', 'deployment',
                'ci/cd', 'devops', 'cloud', 'security', 'authentication', 'database'
            ],
            'data': [
                'analytics', 'visualization', 'machine learning', 'statistics',
                'modeling', 'pipeline', 'etl', 'big data', 'insights', 'metrics',
                'dashboard', 'reporting', 'analysis', 'prediction', 'algorithm'
            ],
            'business': [
                'strategy', 'growth', 'revenue', 'roi', 'kpi', 'stakeholder',
                'process', 'efficiency', 'optimization', 'leadership', 'team',
                'project management', 'budget', 'cost reduction', 'market'
            ]
        }
        
        keywords = []
        text_lower = text.lower()
        
        if domain in domain_keywords:
            for keyword in domain_keywords[domain]:
                if keyword in text_lower:
                    keywords.append(keyword)
        
        return keywords