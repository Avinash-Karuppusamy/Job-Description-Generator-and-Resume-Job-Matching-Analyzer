import streamlit as st
import json
import os
from typing import Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import Unicode utilities for consistent UTF-8 handling
from unicode_utils import clean_unicode_text

from main import ResumeJobMatcher
from config import Config

# Set page config
st.set_page_config(
    page_title="Resume-Job Matching AI Agent",
    page_icon="R",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
    .eligibility-eligible {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .eligibility-maybe {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .eligibility-not {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    .metric-card {
        background: #f7f9fc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'matcher' not in st.session_state:
        st.session_state.matcher = None

def check_api_key():
    """Check if API key is configured"""
    if not Config.OPENAI_API_KEY:
        st.error("⚠️ OpenAI API key not found!")
        st.info("Please set your OPENAI_API_KEY in the .env file or environment variables.")
        return False
    return True

def create_score_gauge(score: float, title: str, color: str = "blue"):
    """Create a gauge chart for scores"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        delta = {'reference': 70},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=0, r=0, t=30, b=0))
    return fig

def display_results(results: Dict[str, Any]):
    """Display analysis results"""
    
    st.markdown('<h1 class="main-header">📊 Analysis Results</h1>', unsafe_allow_html=True)
    
    # Overall Score and Eligibility
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        score = results['scoring_results']['overall_score']
        st.plotly_chart(create_score_gauge(score, "Overall Score"), width='stretch')
    
    with col2:
        eligibility = results['scoring_results']['eligibility_status']
        confidence = results['scoring_results']['confidence_level']
        
        eligibility_class = {
            'ELIGIBLE': 'eligibility-eligible',
            'MAYBE ELIGIBLE': 'eligibility-maybe',
            'NOT ELIGIBLE': 'eligibility-not'
        }.get(eligibility, '')
        
        st.markdown(f"""
        <div class="score-card {eligibility_class}">
            <h2>{eligibility}</h2>
            <p>Confidence: {confidence:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        skills_score = results['scoring_results']['skills_score']
        st.plotly_chart(create_score_gauge(skills_score, "Skills Match", "orange"), width='stretch')
    
    # Detailed Scores
    st.markdown("## 📈 Detailed Scoring Breakdown")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create score comparison chart
        categories = ['Skills', 'Experience', 'Education', 'Certifications']
        scores = [
            results['scoring_results']['skills_score'],
            results['scoring_results']['experience_score'],
            results['scoring_results']['education_score'],
            results['scoring_results']['certifications_score']
        ]
        
        fig = px.bar(
            x=categories,
            y=scores,
            title="Score Breakdown",
            labels={'x': 'Category', 'y': 'Score'},
            color=scores,
            color_continuous_scale='viridis'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        # Candidate and Job Info
        st.markdown("### 👤 Candidate Information")
        st.markdown(f"""
        <div class="metric-card">
            <strong>Name:</strong> {results['candidate_info']['name']}
        </div>
        <div class="metric-card">
            <strong>Email:</strong> {results['candidate_info']['email']}
        </div>
        <div class="metric-card">
            <strong>Phone:</strong> {results['candidate_info']['phone']}
        </div>
        <div class="metric-card">
            <strong>Location:</strong> {results['candidate_info']['location']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 💼 Job Information")
        st.markdown(f"""
        <div class="metric-card">
            <strong>Title:</strong> {results['job_info']['title']}
        </div>
        <div class="metric-card">
            <strong>Company:</strong> {results['job_info']['company']}
        </div>
        <div class="metric-card">
            <strong>Location:</strong> {results['job_info']['location']}
        </div>
        <div class="metric-card">
            <strong>Experience Level:</strong> {results['job_info']['experience_level']}
        </div>
        """, unsafe_allow_html=True)
    
    # Skills Analysis
    st.markdown("## 🔧 Skills Analysis")
    
    skills_details = results['scoring_results']['details']['skills']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Matching Skills")
        matching_skills = skills_details.get('direct_matches', []) + skills_details.get('semantic_matches', [])
        if matching_skills:
            for skill in matching_skills:
                st.success(f"• {skill}")
        else:
            st.info("No matching skills found")
    
    with col2:
        st.markdown("### ❌ Missing Skills")
        missing_skills = skills_details.get('missing_skills', [])
        if missing_skills:
            for skill in missing_skills:
                st.error(f"• {skill}")
        else:
            st.success("All required skills found!")
    
    # Recommendations
    st.markdown("## 💡 Recommendations")
    
    recommendations = results['recommendations']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚀 Next Steps")
        for step in recommendations['next_steps']:
            st.info(f"• {step}")
        
        if recommendations['strengths']:
            st.markdown("### 💪 Strengths")
            for strength in recommendations['strengths']:
                st.success(f"• {strength}")
    
    with col2:
        if recommendations['areas_for_improvement']:
            st.markdown("### 📈 Areas for Improvement")
            for area in recommendations['areas_for_improvement']:
                st.warning(f"• {area}")
        
        if recommendations['interview_tips']:
            st.markdown("### 🎯 Interview Tips")
            for tip in recommendations['interview_tips']:
                st.info(f"• {tip}")
    
    # AutoGen Analysis (if available)
    if results.get('autogen_analysis'):
        st.markdown("## 🤖 AI Agent Analysis")
        
        with st.expander("View Detailed AI Analysis"):
            autogen = results['autogen_analysis']
            
            if 'analysis' in autogen:
                st.markdown("### Resume Analysis")
                st.text(autogen['analysis'].get('resume_analysis', {}).get('analysis', ''))
                
                st.markdown("### Job Analysis")
                st.text(autogen['analysis'].get('job_analysis', {}).get('analysis', ''))
                
                st.markdown("### Matching Analysis")
                st.text(autogen['analysis'].get('matching_analysis', {}).get('analysis', ''))
                
                st.markdown("### Final Assessment")
                st.text(autogen['final_recommendation'].get('assessment', ''))
    
    # Export Results
    st.markdown("## 📁 Export Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download JSON Report"):
            json_str = json.dumps(results, indent=2, ensure_ascii=False, default=str)
            st.download_button(
                label="Download results.json",
                data=json_str,
                file_name="resume_job_analysis.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📋 Download Summary Report"):
            summary = create_summary_report(results)
            st.download_button(
                label="Download summary.txt",
                data=summary,
                file_name="analysis_summary.txt",
                mime="text/plain"
            )

def create_summary_report(results: Dict[str, Any]) -> str:
    """Create a text summary report"""
    
    report = f"""
RESUME-JOB MATCHING ANALYSIS SUMMARY
{'='*50}

CANDIDATE INFORMATION:
Name: {results['candidate_info']['name']}
Email: {results['candidate_info']['email']}
Phone: {results['candidate_info']['phone']}
Location: {results['candidate_info']['location']}

JOB INFORMATION:
Title: {results['job_info']['title']}
Company: {results['job_info']['company']}
Location: {results['job_info']['location']}
Experience Level: {results['job_info']['experience_level']}

SCORING RESULTS:
Overall Score: {results['scoring_results']['overall_score']:.1f}/100
Eligibility Status: {results['scoring_results']['eligibility_status']}
Confidence Level: {results['scoring_results']['confidence_level']:.1f}%

Detailed Scores:
- Skills Match: {results['scoring_results']['skills_score']:.1f}/100
- Experience Match: {results['scoring_results']['experience_score']:.1f}/100
- Education Match: {results['scoring_results']['education_score']:.1f}/100
- Certifications: {results['scoring_results']['certifications_score']:.1f}/100

RECOMMENDATIONS:
Next Steps:
{chr(10).join([f"- {step}" for step in results['recommendations']['next_steps']])}

Strengths:
{chr(10).join([f"- {strength}" for strength in results['recommendations']['strengths']])}

Areas for Improvement:
{chr(10).join([f"- {area}" for area in results['recommendations']['areas_for_improvement']])}

Interview Tips:
{chr(10).join([f"- {tip}" for tip in results['recommendations']['interview_tips']])}
"""
    
    return report

def main():
    """Main Streamlit application"""
    
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Resume-Job Matching AI Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Analyze resume compatibility with job descriptions using AI</p>', unsafe_allow_html=True)
    
    # Check API key
    if not check_api_key():
        st.stop()
    
    # Sidebar
    st.sidebar.title("🔧 Configuration")
    
    # Input Method Selection
    st.sidebar.markdown("### 📝 Input Method")
    input_method = st.sidebar.selectbox(
        "Choose how to input resume and job data:",
        ["Manual Text Input", "File Upload", "Demo Data"]
    )
    
    # Initialize matcher
    if st.session_state.matcher is None:
        with st.spinner("Initializing AI Agent..."):
            st.session_state.matcher = ResumeJobMatcher()
    
    # Main content based on input method
    if input_method == "Manual Text Input":
        st.markdown("## 📝 Manual Input")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Resume")
            resume_text = st.text_area(
                "Paste resume text here:",
                height=400,
                placeholder="Paste the complete resume text here..."
            )
        
        with col2:
            st.markdown("### Job Description")
            job_description = st.text_area(
                "Paste job description here:",
                height=400,
                placeholder="Paste the complete job description here..."
            )
        
        if st.button("🔍 Analyze Match", type="primary"):
            if resume_text and job_description:
                with st.spinner("🤖 Analyzing resume-job compatibility..."):
                    try:
                        # Clean Unicode characters from both texts
                        cleaned_resume = clean_unicode_text(resume_text)
                        cleaned_job = clean_unicode_text(job_description)
                        
                        results = st.session_state.matcher.safe_analyze_match(cleaned_resume, cleaned_job)
                        st.session_state.results = results
                        st.success("✅ Analysis completed successfully!")
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
            else:
                st.error("Please provide both resume and job description")
    
    elif input_method == "File Upload":
        st.markdown("## 📁 File Upload")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Resume File")
            resume_file = st.file_uploader(
                "Upload resume (PDF, DOCX, or TXT)",
                type=['pdf', 'docx', 'txt'],
                key="resume_file"
            )
            
            if resume_file:
                st.success(f"✅ Resume file uploaded: {resume_file.name}")
                
                # Read file content based on type
                try:
                    if resume_file.type == "text/plain":
                        resume_text = resume_file.read().decode('utf-8', errors='ignore')
                    elif resume_file.type == "application/pdf":
                        # Save PDF temporarily and extract text
                        import tempfile
                        import os
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(resume_file.read())
                            tmp_file_path = tmp_file.name
                        
                        # Extract text from PDF
                        from resume_parser import ResumeParser
                        parser = ResumeParser()
                        resume_text = parser._extract_from_pdf(tmp_file_path)
                        os.unlink(tmp_file_path)  # Clean up temp file
                        
                    elif resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        # Save DOCX temporarily and extract text
                        import tempfile
                        import os
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                            tmp_file.write(resume_file.read())
                            tmp_file_path = tmp_file.name
                        
                        # Extract text from DOCX
                        from resume_parser import ResumeParser
                        parser = ResumeParser()
                        resume_text = parser._extract_from_docx(tmp_file_path)
                        os.unlink(tmp_file_path)  # Clean up temp file
                    else:
                        resume_text = resume_file.read().decode('utf-8', errors='ignore')
                    
                    st.info(f"✅ Successfully extracted text from {resume_file.name}")
                    
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
                    resume_text = ""
            else:
                resume_text = ""
        
        with col2:
            st.markdown("### Job Description File")
            job_file = st.file_uploader(
                "Upload job description (TXT, PDF, DOCX)",
                type=['txt', 'pdf', 'docx'],
                key="job_file"
            )
            
            if job_file:
                st.success(f"✅ Job description uploaded: {job_file.name}")
                
                # Read file content based on type
                try:
                    if job_file.type == "text/plain":
                        job_description = job_file.read().decode('utf-8', errors='ignore')
                    elif job_file.type == "application/pdf":
                        # Save PDF temporarily and extract text
                        import tempfile
                        import os
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(job_file.read())
                            tmp_file_path = tmp_file.name
                        
                        # Extract text from PDF
                        from resume_parser import ResumeParser
                        parser = ResumeParser()
                        job_description = parser._extract_from_pdf(tmp_file_path)
                        os.unlink(tmp_file_path)  # Clean up temp file
                        
                    elif job_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        # Save DOCX temporarily and extract text
                        import tempfile
                        import os
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
                            tmp_file.write(job_file.read())
                            tmp_file_path = tmp_file.name
                        
                        # Extract text from DOCX
                        from resume_parser import ResumeParser
                        parser = ResumeParser()
                        job_description = parser._extract_from_docx(tmp_file_path)
                        os.unlink(tmp_file_path)  # Clean up temp file
                    else:
                        job_description = job_file.read().decode('utf-8', errors='ignore')
                    
                    st.info(f"✅ Successfully extracted text from {job_file.name}")
                    
                except Exception as e:
                    st.error(f"❌ Error reading job description file: {str(e)}")
                    job_description = ""
            else:
                job_description = ""
        
        if st.button("🔍 Analyze Match", type="primary"):
            if resume_file and job_file:
                with st.spinner("🤖 Analyzing resume-job compatibility..."):
                    try:
                        # Clean Unicode characters from both texts
                        cleaned_resume = clean_unicode_text(resume_text)
                        cleaned_job = clean_unicode_text(job_description)
                        
                        results = st.session_state.matcher.safe_analyze_match(cleaned_resume, cleaned_job)
                        st.session_state.results = results
                        st.success("✅ Analysis completed successfully!")
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {str(e)}")
            else:
                st.error("Please upload both resume and job description files")
    
    else:  # Demo Data
        st.markdown("## 🎭 Demo Mode")
        st.info("This will run the analysis with sample resume and job description data.")
        
        if st.button("🚀 Run Demo Analysis", type="primary"):
            with st.spinner("🤖 Running demo analysis..."):
                try:
                    # Get sample data
                    from main import get_sample_resume, get_sample_job_description
                    resume_text = get_sample_resume()
                    job_description = get_sample_job_description()
                    
                    # Clean Unicode characters from both texts
                    cleaned_resume = clean_unicode_text(resume_text)
                    cleaned_job = clean_unicode_text(job_description)
                    
                    results = st.session_state.matcher.safe_analyze_match(cleaned_resume, cleaned_job)
                    st.session_state.results = results
                    st.success("✅ Demo analysis completed successfully!")
                except Exception as e:
                    st.error(f"❌ Error during demo analysis: {str(e)}")
    
    # Display results if available
    if st.session_state.results:
        display_results(st.session_state.results)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">Powered by AutoGen AI | Resume-Job Matching Agent v1.0</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
