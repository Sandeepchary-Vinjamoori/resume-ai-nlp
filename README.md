# 🚀 Resume AI - Advanced NLP-Based Resume Generation System

An intelligent resume generation platform that transforms natural language input into professional, ATS-optimized resumes using advanced NLP processing and optional AI enhancement.

## ✨ Key Features

### 🧠 Advanced NLP Processing
- **True Linguistic Analysis**: spaCy-based tokenization, POS tagging, and semantic analysis
- **Action Verb Transformation**: Automatically converts weak verbs to strong action verbs
- **Active Voice Conversion**: Eliminates passive voice constructions
- **Quantified Achievement Extraction**: Identifies and enhances metrics and achievements
- **Technical Skill Recognition**: 500+ skill database with intelligent categorization

### 🤖 Optional AI Enhancement (NEW!)
- **Hybrid Architecture**: Local NLP + Optional OpenAI polishing
- **Cost-Optimized**: Uses `gpt-4o-mini` for efficient text refinement
- **Graceful Fallback**: Works perfectly without API key
- **Token-Efficient**: Smart text length validation and minimal API usage

### 📄 Professional Output
- **ATS-Optimized Formatting**: Perfect compatibility with Applicant Tracking Systems
- **Multi-Format Export**: DOCX and PDF with professional styling
- **Recruiter-Grade Quality**: Professional summaries and bullet points
- **Multi-Page Support**: Handles extensive content with proper pagination

## 🏗️ Architecture

```
User Input (Natural Language)
    ↓
Local NLP Processing (spaCy)
    ↓
Content Enhancement (Rule-based)
    ↓
Optional AI Polishing (OpenAI)
    ↓
ATS-Optimized Resume Output
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd resume_ai

# Install dependencies
pip install -r requirements.txt

# Optional: Install spaCy model for enhanced NLP
python -m spacy download en_core_web_sm
```

### 2. Basic Usage (Local Processing Only)

```bash
# Start the application
python app.py

# Visit http://localhost:5000 in your browser
```

The system works perfectly without any API keys using advanced local NLP processing.

### 3. Enhanced Usage (With AI Polishing)

```bash
# Set your OpenAI API key (optional)
export OPENAI_API_KEY="your-api-key-here"

# Start the application
python app.py
```

With an API key, the system adds AI polishing for even better text quality.

## 🧪 Testing

### Run All Tests
```bash
python test_app.py              # Core functionality
python test_openai_integration.py  # AI integration
python demo_openai.py           # Interactive demo
```

### Test Results
```
📊 Test Results: 4/4 tests passed
✅ Local NLP processing
✅ AI enhancement (when available)
✅ ATS formatting
✅ Export functionality
```

## 🎯 Content Transformation Examples

### Experience Bullets
**Input:**
```
worked on java project
helped with database optimization
```

**Local NLP Output:**
```
• Developed Java project, demonstrating programming skills
• Implemented database optimization, improving system performance
```

**AI-Enhanced Output:**
```
• Developed a comprehensive Java-based project, enhancing functionality and performance
• Implemented database optimization strategies, resulting in improved query efficiency and reduced latency
```

### Professional Summary
**Input:**
```
Software engineer with 5 years experience looking for opportunities
```

**AI-Enhanced Output:**
```
Results-driven software engineer with over 5 years of experience in full-stack development. 
Proven expertise in delivering innovative software solutions with a track record of improving 
system performance and user engagement. Seeking to leverage technical skills and leadership 
experience to drive innovation at a forward-thinking technology company.
```

## 🔧 Configuration

### Environment Variables
```bash
# Optional - enables AI polishing
OPENAI_API_KEY="your-api-key-here"

# Optional - custom model (default: gpt-4o-mini)
OPENAI_MODEL="gpt-4o-mini"
```

### Supported Styles
- `modern` (default): Clean, professional layout
- `simple`: Minimalist design
- `academic`: Traditional academic format

### Supported Formats
- `docx`: Microsoft Word format
- `pdf`: Portable Document Format

## 📊 Performance & Cost

### Token Usage (with OpenAI)
- **Model**: `gpt-4o-mini` (cost-efficient)
- **Average Cost**: ~$0.01-0.05 per resume
- **Smart Optimization**: Skips short text, validates length
- **Fallback**: Always works without API

### Processing Speed
- **Local NLP**: ~0.5-1 second per resume
- **With AI**: ~2-4 seconds per resume
- **Export**: ~1-2 seconds per file

## 🛡️ Reliability Features

### Graceful Degradation
- Works without internet connection
- Handles missing dependencies
- Automatic fallback to text export
- Error recovery and logging

### Quality Assurance
- Input validation and sanitization
- Output format verification
- Comprehensive error handling
- Detailed logging for debugging

## 🎨 Web Interface Features

### Modern UI
- Responsive design for all devices
- Real-time preview functionality
- Interactive form with validation
- Progress indicators and feedback

### User Experience
- Step-by-step wizard interface
- Inline help and tooltips
- Error messages and guidance
- Download management

## 📁 Project Structure

```
resume_ai/
├── app.py                 # Flask web application
├── core/
│   ├── nlp_engine.py     # NLP processing engine
│   ├── content_enhancer.py  # Content transformation + AI
│   ├── resume_builder.py    # Resume assembly
│   └── simple_exporter.py   # Export functionality
├── templates/            # HTML templates
├── static/              # CSS, JS, images
├── tests/               # Test files
└── generated/           # Output directory
```

## 🔍 API Reference

### ContentEnhancer Class
```python
from core.content_enhancer import ContentEnhancer

enhancer = ContentEnhancer()

# Transform experience bullets
enhanced = enhancer.enhance_experience("worked on web app")

# Generate professional summary
summary = enhancer.enhance_summary("software engineer with 5 years experience")

# AI polishing (if API key available)
polished = enhancer.ai_polish(text, content_type='experience')
```

### Resume Builder
```python
from core.resume_builder import ResumeBuilder

builder = ResumeBuilder()
resume_text = builder.build_resume(form_data, style='modern')
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **spaCy**: Advanced NLP processing
- **OpenAI**: AI text enhancement
- **Flask**: Web framework
- **ReportLab**: PDF generation
- **python-docx**: Word document creation

---

**Built with ❤️ for job seekers everywhere**

Transform your career story into a professional resume that gets noticed by both ATS systems and human recruiters.