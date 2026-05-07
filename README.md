# Resume-Job Matching AI Agent

An intelligent AI-powered system that evaluates resume eligibility against job descriptions using AutoGen framework and advanced scoring algorithms.

## 🚀 Features

- **AI-Powered Analysis**: Uses AutoGen agents for comprehensive resume-job matching
- **Advanced Scoring Engine**: Multi-factor scoring with weighted criteria
- **Intelligent Parsing**: Extracts key information from resumes and job descriptions
- **Multiple Input Methods**: Support for text input, file uploads (PDF/DOCX), and demo data
- **Web Interface**: Beautiful Streamlit-based user interface
- **Detailed Reports**: Comprehensive analysis with actionable recommendations
- **Export Options**: Download results as JSON or text reports

## 📋 System Requirements

- Python 3.8+
- OpenAI API key
- 8GB+ RAM recommended

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd "Autogen gen 1resume- desc"
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

5. **Download spaCy model**
```bash
python -m spacy download en_core_web_sm
```

## 🎯 Quick Start

### Option 1: Web Interface (Recommended)

```bash
streamlit run app.py
```

Open your browser and navigate to `http://localhost:8501`

### Option 2: Command Line Interface

```bash
python main.py
```

Follow the interactive prompts to analyze resumes against job descriptions.

## 📊 How It Works

### 1. Resume Parsing
- Extracts personal information, skills, experience, education, and certifications
- Supports PDF, DOCX, and text formats
- Identifies key qualifications and achievements

### 2. Job Description Parsing
- Analyzes job requirements, responsibilities, and qualifications
- Identifies required skills, experience level, and education
- Extracts company and role information

### 3. AI Agent Analysis
- **Resume Analyst**: Evaluates candidate qualifications and experience
- **Job Analyst**: Analyzes job requirements and role complexity
- **Matching Specialist**: Compares resume against job requirements
- **Eligibility Assessor**: Makes final hiring recommendations

### 4. Scoring Engine
- **Skills Match (40%)**: Technical skills and competencies
- **Experience Match (30%)**: Years and relevance of experience
- **Education Match (20%)**: Educational background and qualifications
- **Certifications (10%)**: Professional certifications and credentials

### 5. Recommendations
- Eligibility determination (Eligible/Maybe Eligible/Not Eligible)
- Next steps in hiring process
- Strengths and areas for improvement
- Interview preparation tips

## 📁 Project Structure

```
├── app.py                 # Streamlit web application
├── main.py               # Command-line interface
├── config.py             # Configuration settings
├── resume_parser.py      # Resume parsing logic
├── job_parser.py         # Job description parsing
├── autogen_agents.py     # AutoGen AI agents
├── scoring_engine.py     # Scoring and evaluation logic
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── examples/            # Sample resumes and job descriptions
│   ├── sample_resume_1.txt
│   ├── sample_resume_2.txt
│   ├── sample_job_1.txt
│   └── sample_job_2.txt
└── README.md           # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Optional (for Azure OpenAI)
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_VERSION=2023-12-01-preview
```

### Scoring Weights

You can adjust the scoring weights in `config.py`:

```python
SKILLS_WEIGHT = 0.4
EXPERIENCE_WEIGHT = 0.3
EDUCATION_WEIGHT = 0.2
CERTIFICATIONS_WEIGHT = 0.1
ELIGIBILITY_THRESHOLD = 0.7
```

## 📈 Usage Examples

### Web Interface

1. **Manual Input**: Paste resume and job description text directly
2. **File Upload**: Upload PDF/DOCX resume and text job description
3. **Demo Mode**: Use built-in sample data for testing

### Command Line

```bash
# Interactive mode
python main.py

# Choose input method:
# 1. Enter resume text manually
# 2. Load resume from file
# 3. Run demo with sample data
```

### Programmatic Usage

```python
from main import ResumeJobMatcher

# Initialize matcher
matcher = ResumeJobMatcher()

# Analyze match
results = matcher.analyze_match(resume_text, job_description)

# Print results
matcher.print_results(results)

# Save results
matcher.save_results(results, "analysis_results.json")
```

## 🎨 Features in Detail

### Advanced Scoring

- **Semantic Skill Matching**: Recognizes related skills and synonyms
- **Experience Level Assessment**: Evaluates years and relevance of experience
- **Education Matching**: Considers degree levels and field of study
- **Certification Verification**: Matches required professional certifications

### AI Agent Analysis

Each AutoGen agent provides specialized analysis:

1. **Resume Analyst**: Deep dive into candidate qualifications
2. **Job Analyst**: Comprehensive job requirement analysis
3. **Matching Specialist**: Detailed compatibility assessment
4. **Eligibility Assessor**: Final hiring recommendations

### Interactive Dashboard

- Real-time analysis progress
- Visual score representations
- Detailed breakdowns and insights
- Export capabilities
- Responsive design for all devices

## 🔍 Example Results

The system provides comprehensive analysis including:

```
📊 OVERALL SCORE: 85.2/100
🎯 ELIGIBILITY STATUS: ELIGIBLE
🔍 CONFIDENCE LEVEL: 87.5%

📊 DETAILED SCORES:
   Skills Match: 90.0/100
   Experience Match: 85.0/100
   Education Match: 80.0/100
   Certifications: 75.0/100

🔧 SKILLS ANALYSIS:
   Direct Matches: Python, Machine Learning, SQL, AWS
   Missing Skills: None

💡 RECOMMENDATIONS:
   Next Steps: Schedule technical interview, Prepare for behavioral questions
   Strengths: Strong technical skills alignment, Relevant experience level
```

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run web app
streamlit run app.py

# Or run CLI
python main.py
```

### Production Deployment

For production deployment, consider:

1. **Docker**: Containerize the application
2. **Cloud Hosting**: Deploy on AWS, Google Cloud, or Azure
3. **Load Balancing**: Handle multiple concurrent analyses
4. **Database**: Store analysis results and user data
5. **Monitoring**: Track performance and errors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the [Issues](../../issues) page
2. Create a new issue with detailed description
3. Include error messages and system information

## 🔄 Updates

- **v1.0**: Initial release with core functionality
- **v1.1**: Enhanced parsing and scoring algorithms
- **v1.2**: Web interface and visualizations
- **v1.3**: Multiple file format support

## 🎯 Roadmap

- [ ] Integration with ATS systems
- [ ] Bulk resume processing
- [ ] Custom scoring models
- [ ] Multi-language support
- [ ] Mobile application
- [ ] API endpoints for integration

---

**Built with ❤️ using AutoGen, Streamlit, and modern AI technologies**
