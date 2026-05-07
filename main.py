#!/usr/bin/env python3
"""
Resume-Job Matching AI Agent using AutoGen
Main application entry point
"""

import os
import sys
import json
from typing import Dict, Any
from dataclasses import asdict

# Import Unicode utilities for consistent UTF-8 handling
from unicode_utils import clean_unicode_text, safe_print, safe_file_read, safe_file_write

from autogen_agents import ResumeJobMatchingAgents
from scoring_engine import ScoringEngine
from resume_parser import ResumeParser
from job_parser import JobParser
from config import Config

class ResumeJobMatcher:
    """Main application class for resume-job matching"""
    
    def __init__(self):
        self.config = Config()
        self.resume_parser = ResumeParser()
        self.job_parser = JobParser()
        self.scoring_engine = ScoringEngine()
        
        # Initialize AutoGen agents (temporarily disabled due to Unicode issues)
        try:
            # self.agents = ResumeJobMatchingAgents(
            #     api_key=self.config.OPENAI_API_KEY,
            #     model=self.config.OPENAI_MODEL
            # )
            self.agents = None  # Temporarily disabled
            safe_print("AutoGen agents temporarily disabled due to Unicode compatibility issues")
        except Exception as e:
            safe_print(f"Warning: Could not initialize AutoGen agents: {e}")
            self.agents = None
    
    def safe_analyze_match(self, resume_input: str, job_description: str, is_file_path: bool = False) -> Dict[str, Any]:
        """Safe analyze resume against job description with Unicode error handling"""
        
        try:
            return self.analyze_match(resume_input, job_description, is_file_path)
        except UnicodeEncodeError as e:
            safe_print(f"Unicode error detected: {e}")
            safe_print("Attempting with ASCII-only processing...")
            
            # Force ASCII-only processing
            resume_input = resume_input.encode('ascii', errors='ignore').decode('ascii')
            job_description = job_description.encode('ascii', errors='ignore').decode('ascii')
            
            return self.analyze_match(resume_input, job_description, is_file_path)
        except Exception as e:
            safe_print(f"Analysis failed: {e}")
            raise

    def analyze_match(self, resume_input: str, job_description: str, is_file_path: bool = False) -> Dict[str, Any]:
        """Analyze resume against job description"""
        
        safe_print("Starting Resume-Job Matching Analysis...")
        
        # Clean Unicode characters from inputs
        resume_input = clean_unicode_text(resume_input)
        job_description = clean_unicode_text(job_description)
        
        # Parse resume
        if is_file_path:
            safe_print("Parsing resume file...")
            resume_data = self.resume_parser.parse_resume(resume_input)
        else:
            safe_print("Parsing resume text...")
            resume_data = self.resume_parser.parse_resume_text(resume_input)
        
        # Parse job description
        safe_print("Parsing job description...")
        job_data = self.job_parser.parse_job(job_description)
        
        # Calculate scoring engine results
        safe_print("Calculating compatibility scores...")
        scoring_result = self.scoring_engine.calculate_match_score(resume_data, job_data)
        
        # Get AutoGen analysis if available
        autogen_analysis = None
        if self.agents:
            safe_print("Running AI agent analysis...")
            try:
                autogen_analysis = self.agents.analyze_resume_job_match(
                    resume_input if not is_file_path else self.resume_parser._extract_text(resume_input),
                    job_description
                )
            except Exception as e:
                safe_print(f"AutoGen analysis failed: {e}")
        
        # Compile comprehensive results
        results = {
            "candidate_info": {
                "name": resume_data.name,
                "email": resume_data.email,
                "phone": resume_data.phone,
                "location": resume_data.location
            },
            "job_info": {
                "title": job_data.title,
                "company": job_data.company,
                "location": job_data.location,
                "experience_level": job_data.experience_level
            },
            "scoring_results": {
                "overall_score": scoring_result.overall_score,
                "skills_score": scoring_result.skills_score,
                "experience_score": scoring_result.experience_score,
                "education_score": scoring_result.education_score,
                "certifications_score": scoring_result.certifications_score,
                "eligibility_status": scoring_result.eligibility_status,
                "confidence_level": scoring_result.confidence_level,
                "details": {
                    "skills": scoring_result.skills_details,
                    "experience": scoring_result.experience_details,
                    "education": scoring_result.education_details,
                    "certifications": scoring_result.certifications_details
                }
            },
            "autogen_analysis": autogen_analysis,
            "recommendations": self._generate_recommendations(scoring_result, resume_data, job_data)
        }
        
        safe_print("✅ Analysis complete!")
        return results
    
    def _generate_recommendations(self, scoring_result, resume_data, job_data) -> Dict[str, Any]:
        """Generate recommendations based on analysis"""
        
        recommendations = {
            "next_steps": [],
            "strengths": [],
            "areas_for_improvement": [],
            "interview_tips": []
        }
        
        # Next steps based on eligibility
        if scoring_result.eligibility_status == "ELIGIBLE":
            recommendations["next_steps"].extend([
                "Schedule technical interview",
                "Prepare for behavioral questions",
                "Conduct reference check",
                "Review portfolio/work samples"
            ])
        elif scoring_result.eligibility_status == "MAYBE ELIGIBLE":
            recommendations["next_steps"].extend([
                "Conduct phone screening to clarify gaps",
                "Assess learning potential and attitude",
                "Consider skill assessment test",
                "Evaluate cultural fit"
            ])
        else:
            recommendations["next_steps"].extend([
                "Reject application or consider for different role",
                "Provide feedback on missing requirements",
                "Consider for junior position if applicable"
            ])
        
        # Strengths
        if scoring_result.skills_score >= 80:
            recommendations["strengths"].append("Strong technical skills alignment")
        if scoring_result.experience_score >= 80:
            recommendations["strengths"].append("Relevant experience level")
        if scoring_result.education_score >= 80:
            recommendations["strengths"].append("Meets educational requirements")
        
        # Areas for improvement
        if scoring_result.skills_score < 60:
            missing_skills = scoring_result.skills_details.get('missing_skills', [])
            if missing_skills:
                recommendations["areas_for_improvement"].append(f"Develop missing skills: {', '.join(missing_skills[:3])}")
        
        if scoring_result.experience_score < 60:
            recommendations["areas_for_improvement"].append("Gain more relevant experience")
        
        # Interview tips
        if scoring_result.skills_score >= 70:
            recommendations["interview_tips"].append("Focus on technical problem-solving questions")
        if scoring_result.experience_score >= 70:
            recommendations["interview_tips"].append("Prepare to discuss past projects and achievements")
        
        return recommendations
    
    def safe_print_results(self, results: Dict[str, Any]):
        """Print formatted results"""
        
        safe_print("\n" + "="*60)
        safe_print("RESUME-JOB MATCHING ANALYSIS REPORT")
        safe_print("="*60)
        
        # Candidate and Job Info
        safe_print(f"\nCANDIDATE: {results['candidate_info']['name']}")
        safe_print(f"Email: {results['candidate_info']['email']}")
        safe_print(f"Phone: {results['candidate_info']['phone']}")
        safe_print(f"Location: {results['candidate_info']['location']}")
        
        safe_print(f"\nJOB: {results['job_info']['title']}")
        safe_print(f"Company: {results['job_info']['company']}")
        safe_print(f"Location: {results['job_info']['location']}")
        safe_print(f"Experience Level: {results['job_info']['experience_level']}")
        
        # Scoring Results
        safe_print(f"\nOVERALL SCORE: {results['scoring_results']['overall_score']:.1f}/100")
        safe_print(f"ELIGIBILITY STATUS: {results['scoring_results']['eligibility_status']}")
        safe_print(f"CONFIDENCE LEVEL: {results['scoring_results']['confidence_level']:.1f}%")
        
        safe_print(f"\nDETAILED SCORES:")
        safe_print(f"   Skills Match: {results['scoring_results']['skills_score']:.1f}/100")
        safe_print(f"   Experience Match: {results['scoring_results']['experience_score']:.1f}/100")
        safe_print(f"   Education Match: {results['scoring_results']['education_score']:.1f}/100")
        safe_print(f"   Certifications: {results['scoring_results']['certifications_score']:.1f}/100")
        
        # Skills Details
        skills_details = results['scoring_results']['details']['skills']
        safe_print(f"\nSKILLS ANALYSIS:")
        safe_print(f"   Direct Matches: {', '.join(skills_details.get('direct_matches', []))}")
        safe_print(f"   Missing Skills: {', '.join(skills_details.get('missing_skills', []))}")
        
        # Recommendations
        recommendations = results['recommendations']
        safe_print(f"\nRECOMMENDATIONS:")
        safe_print(f"   Next Steps: {', '.join(recommendations['next_steps'])}")
        if recommendations['strengths']:
            safe_print(f"   Strengths: {', '.join(recommendations['strengths'])}")
        if recommendations['areas_for_improvement']:
            safe_print(f"   Areas for Improvement: {', '.join(recommendations['areas_for_improvement'])}")
        
        safe_print("\n" + "="*60)
    
    def save_results(self, results: Dict[str, Any], filename: str):
        """Save results to JSON file"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        safe_print(f"📁 Results saved to: {filename}")

def main():
    """Main function for command-line interface"""
    
    safe_print("Resume-Job Matching AI Agent")
    safe_print("="*50)
    
    # Check for API key
    if not Config.OPENAI_API_KEY:
        safe_print("Error: OPENAI_API_KEY not found in environment variables.")
        safe_print("Please set your OpenAI API key in the .env file or environment variables.")
        return
    
    # Initialize matcher
    matcher = ResumeJobMatcher()
    
    # Get input method
    safe_print("\nChoose input method:")
    safe_print("1. Enter resume text manually")
    safe_print("2. Load resume from file (PDF/DOCX)")
    safe_print("3. Run demo with sample data")
        
    choice = input("\nEnter your choice (1-3): ").strip()
        
    if choice == "1":
        # Manual text input
        safe_print("\nEnter resume text (press Enter twice to finish):")
        resume_lines = []
        while True:
            line = input()
            if line == "" and len(resume_lines) > 0 and resume_lines[-1] == "":
                break
            resume_lines.append(line)
        resume_text = "\n".join(resume_lines[:-1])  # Remove last empty line
            
        safe_print("\nEnter job description (press Enter twice to finish):")
        job_lines = []
        while True:
            line = input()
            if line == "" and len(job_lines) > 0 and job_lines[-1] == "":
                break
            job_lines.append(line)
        job_description = "\n".join(job_lines[:-1])  # Remove last empty line
            
    elif choice == "2":
        # File input
        resume_file = input("\nEnter resume file path: ").strip()
        if not os.path.exists(resume_file):
            safe_print(f"Error: Resume file not found: {resume_file}")
            return
            
        job_file = input("Enter job description file path: ").strip()
        if not os.path.exists(job_file):
            safe_print(f"Error: Job description file not found: {job_file}")
            return
            
        # Read files
        resume_text = safe_file_read(resume_file)
        job_description = safe_file_read(job_file)
        
    elif choice == "3":
        # Demo with sample data
        safe_print("\nRunning demo with sample data...")
        resume_text = get_sample_resume()
        job_description = get_sample_job_description()
        
    else:
        safe_print("Invalid choice")
        return
        
    # Run analysis
    try:
        results = matcher.analyze_match(resume_text, job_description)
            
        # Display results
        matcher.safe_print_results(results)
        
        # Save results
        save_choice = input("\nSave results to file? (y/n): ").strip().lower()
        if save_choice == 'y':
            filename = input("Enter filename (default: results.json): ").strip()
            if not filename:
                filename = "results.json"
            matcher.save_results(results, filename)
        
    except Exception as e:
        safe_print(f"Error during analysis: {e}")
        import traceback
        traceback.safe_print_exc()

def get_sample_resume() -> str:
    """Get sample resume for demo"""
    return """
John Doe
Email: john.doe@email.com | Phone: (555) 123-4567 | Location: San Francisco, CA

SUMMARY
Experienced Software Engineer with 5+ years of experience in full-stack development.
Proficient in Python, JavaScript, and modern web technologies. Strong background in
cloud computing and DevOps practices.

SKILLS
Programming Languages: Python, JavaScript, Java, SQL
Web Technologies: React, Node.js, HTML, CSS, Django
Cloud Platforms: AWS, Azure
Databases: PostgreSQL, MongoDB, Redis
DevOps: Docker, Kubernetes, Git, CI/CD
Other: Agile, Scrum, Machine Learning

EXPERIENCE
Senior Software Engineer | Tech Corp | San Francisco, CA | 2020-Present
- Developed and maintained microservices architecture using Python and Django
- Led migration of monolithic application to containerized microservices
- Implemented CI/CD pipelines using Jenkins and Docker
- Mentored junior developers and conducted code reviews

Software Engineer | StartupXYZ | Mountain View, CA | 2018-2020
- Built RESTful APIs using Node.js and Express
- Developed responsive web applications using React
- Worked with PostgreSQL and MongoDB databases
- Participated in agile development processes

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2014-2018

CERTIFICATIONS
AWS Certified Solutions Architect
Certified Kubernetes Administrator (CKA)
"""

def get_sample_job_description() -> str:
    """Get sample job description for demo"""
    return """
Senior Software Engineer
Company: Tech Innovations Inc.
Location: San Francisco, CA | Remote Option Available

Job Description:
We are seeking a Senior Software Engineer to join our growing engineering team.
You will be responsible for designing, developing, and maintaining scalable
web applications and services.

Responsibilities:
- Design and implement scalable microservices architecture
- Develop RESTful APIs and web applications
- Lead technical projects and mentor junior engineers
- Implement DevOps best practices and CI/CD pipelines
- Collaborate with cross-functional teams

Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- Experience with React, Node.js, and modern web frameworks
- Hands-on experience with cloud platforms (AWS preferred)
- Knowledge of containerization technologies (Docker, Kubernetes)
- Bachelor's degree in Computer Science or related field
- Experience with agile development methodologies

Preferred Qualifications:
- AWS or Azure certification
- Experience with machine learning
- Previous leadership or mentoring experience
- Contribution to open-source projects

We offer competitive salary, comprehensive benefits, and flexible work arrangements.
"""

if __name__ == "__main__":
    main()
