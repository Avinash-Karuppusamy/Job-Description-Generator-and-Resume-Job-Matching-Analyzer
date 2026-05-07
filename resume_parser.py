import re
import json
from typing import Dict, List, Any
from dataclasses import dataclass
import docx
import PyPDF2
import spacy

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy model not found. Run: python -m spacy download en_core_web_sm")
    nlp = None

@dataclass
class ResumeData:
    """Data class to store parsed resume information"""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: List[str] = None
    experience: List[Dict[str, Any]] = None
    education: List[Dict[str, Any]] = None
    certifications: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.experience is None:
            self.experience = []
        if self.education is None:
            self.education = []
        if self.certifications is None:
            self.certifications = []

class ResumeParser:
    """Parser for extracting information from resume documents"""
    
    def __init__(self):
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
    def parse_resume(self, file_path: str) -> ResumeData:
        """Parse resume from file (PDF or DOCX)"""
        text = self._extract_text(file_path)
        return self._parse_text(text)
    
    def parse_resume_text(self, text: str) -> ResumeData:
        """Parse resume from text string"""
        return self._parse_text(text)
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        if file_path.endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            return self._extract_from_docx(file_path)
        else:
            raise ValueError("Unsupported file format. Use PDF or DOCX.")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _parse_text(self, text: str) -> ResumeData:
        """Parse resume text and extract structured information"""
        resume_data = ResumeData()
        
        # Basic information extraction
        resume_data.email = self._extract_email(text)
        resume_data.phone = self._extract_phone(text)
        resume_data.name = self._extract_name(text)
        
        # Section-based extraction
        sections = self._split_into_sections(text)
        
        resume_data.summary = sections.get('summary', '')
        resume_data.skills = self._extract_skills(sections.get('skills', ''))
        resume_data.experience = self._extract_experience(sections.get('experience', ''))
        resume_data.education = self._extract_education(sections.get('education', ''))
        resume_data.certifications = self._extract_certifications(sections.get('certifications', ''))
        
        return resume_data
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from text"""
        match = re.search(self.email_pattern, text)
        return match.group() if match else ""
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        match = re.search(self.phone_pattern, text)
        return match.group() if match else ""
    
    def _extract_name(self, text: str) -> str:
        """Extract name from text (basic implementation)"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first few lines
            line = line.strip()
            if len(line.split()) >= 2 and len(line) < 50:
                # Likely a name line
                if not re.search(r'\d|@|\.', line):
                    return line
        return ""
    
    def _split_into_sections(self, text: str) -> Dict[str, str]:
        """Split resume text into sections"""
        sections = {}
        current_section = ""
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip().lower()
            
            # Check if this is a section header
            if any(keyword in line for keyword in [
                'summary', 'objective', 'profile', 'about',
                'skills', 'technical skills', 'competencies',
                'experience', 'work experience', 'employment', 'professional experience',
                'education', 'academic', 'qualification',
                'certifications', 'certificates', 'credentials'
            ]):
                # Save previous section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                
                # Start new section
                current_section = line
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_skills(self, skills_text: str) -> List[str]:
        """Extract skills from skills section"""
        if not skills_text:
            return []
        
        # Split by common delimiters
        skills = re.split(r'[,;•\n]', skills_text)
        skills = [skill.strip() for skill in skills if skill.strip()]
        
        # Filter out non-skill entries
        filtered_skills = []
        for skill in skills:
            if len(skill) > 2 and len(skill) < 50:
                filtered_skills.append(skill)
        
        return filtered_skills
    
    def _extract_experience(self, experience_text: str) -> List[Dict[str, Any]]:
        """Extract work experience information"""
        if not experience_text:
            return []
        
        experiences = []
        # Basic implementation - split by common patterns
        entries = re.split(r'\n\n|\n(?=[A-Z])', experience_text)
        
        for entry in entries:
            entry = entry.strip()
            if len(entry) > 20:  # Filter out very short entries
                experiences.append({
                    'description': entry,
                    'duration': self._extract_duration(entry),
                    'company': self._extract_company(entry)
                })
        
        return experiences
    
    def _extract_education(self, education_text: str) -> List[Dict[str, Any]]:
        """Extract education information"""
        if not education_text:
            return []
        
        education = []
        entries = re.split(r'\n\n|\n(?=[A-Z])', education_text)
        
        for entry in entries:
            entry = entry.strip()
            if len(entry) > 20:
                education.append({
                    'description': entry,
                    'degree': self._extract_degree(entry),
                    'institution': self._extract_institution(entry)
                })
        
        return education
    
    def _extract_certifications(self, cert_text: str) -> List[str]:
        """Extract certifications"""
        if not cert_text:
            return []
        
        certs = re.split(r'[,;•\n]', cert_text)
        return [cert.strip() for cert in certs if cert.strip() and len(cert.strip()) > 3]
    
    def _extract_duration(self, text: str) -> str:
        """Extract duration from experience entry"""
        # Look for date patterns
        date_pattern = r'(\d{1,2}/\d{4}|\d{4}|\w+ \d{4})'
        matches = re.findall(date_pattern, text)
        return ' - '.join(matches[:2]) if matches else ""
    
    def _extract_company(self, text: str) -> str:
        """Extract company name from experience entry"""
        # Basic implementation - look for company indicators
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['inc', 'llc', 'ltd', 'corp', 'company']):
                return line.strip()
        return ""
    
    def _extract_degree(self, text: str) -> str:
        """Extract degree from education entry"""
        degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma']
        for keyword in degree_keywords:
            if keyword in text.lower():
                return text.strip()
        return ""
    
    def _extract_institution(self, text: str) -> str:
        """Extract institution name from education entry"""
        # Basic implementation
        lines = text.split('\n')
        for line in lines:
            if 'university' in line.lower() or 'college' in line.lower():
                return line.strip()
        return ""
