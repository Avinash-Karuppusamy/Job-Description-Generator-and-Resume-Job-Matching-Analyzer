import re
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class JobData:
    """Data class to store parsed job description information"""
    title: str = ""
    company: str = ""
    location: str = ""
    description: str = ""
    requirements: List[str] = None
    responsibilities: List[str] = None
    skills_required: List[str] = None
    experience_level: str = ""
    education_required: str = ""
    salary: str = ""
    job_type: str = ""
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = []
        if self.responsibilities is None:
            self.responsibilities = []
        if self.skills_required is None:
            self.skills_required = []

class JobParser:
    """Parser for extracting information from job descriptions"""
    
    def __init__(self):
        self.experience_keywords = {
            'entry': ['entry level', 'junior', '0-1', '0 to 1', 'fresher', 'recent graduate'],
            'mid': ['mid level', 'intermediate', '2-5', '2 to 5', '3-5', '3 to 5'],
            'senior': ['senior', 'lead', '5+', '5 to 10', '7+', '7 to 10'],
            'executive': ['executive', 'director', 'vp', 'c-level', '10+', '10+ years']
        }
        
        self.education_keywords = {
            'high_school': ['high school', 'ged', 'diploma'],
            'bachelor': ['bachelor', 'bs', 'ba', 'undergraduate', '4-year'],
            'master': ['master', 'ms', 'ma', 'graduate', 'mba'],
            'phd': ['phd', 'doctorate', 'doctoral', 'ph.d']
        }
    
    def parse_job(self, job_text: str) -> JobData:
        """Parse job description from text"""
        job_data = JobData()
        
        # Extract basic information
        job_data.title = self._extract_title(job_text)
        job_data.company = self._extract_company(job_text)
        job_data.location = self._extract_location(job_text)
        job_data.description = self._extract_description(job_text)
        
        # Extract structured information
        job_data.requirements = self._extract_requirements(job_text)
        job_data.responsibilities = self._extract_responsibilities(job_text)
        job_data.skills_required = self._extract_skills(job_text)
        job_data.experience_level = self._extract_experience_level(job_text)
        job_data.education_required = self._extract_education_required(job_text)
        job_data.salary = self._extract_salary(job_text)
        job_data.job_type = self._extract_job_type(job_text)
        
        return job_data
    
    def _extract_title(self, text: str) -> str:
        """Extract job title"""
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            # Look for common job title patterns
            if any(keyword in line.lower() for keyword in [
                'engineer', 'developer', 'manager', 'analyst', 'specialist',
                'coordinator', 'director', 'associate', 'consultant', 'architect'
            ]) and len(line) < 100:
                return line
        return ""
    
    def _extract_company(self, text: str) -> str:
        """Extract company name"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if any(keyword in line.lower() for keyword in [
                'inc', 'llc', 'ltd', 'corp', 'company', 'technologies', 'systems'
            ]) and len(line) < 100:
                return line
        return ""
    
    def _extract_location(self, text: str) -> str:
        """Extract job location"""
        # Look for location patterns
        location_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}|[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        matches = re.findall(location_pattern, text)
        for match in matches:
            if len(match) < 50 and not any(keyword in match.lower() for keyword in ['required', 'experience', 'skills']):
                return match
        return ""
    
    def _extract_description(self, text: str) -> str:
        """Extract job description"""
        # Look for description section
        lines = text.split('\n')
        description_lines = []
        in_description = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we're entering description section
            if any(keyword in line_lower for keyword in [
                'description', 'about the role', 'position summary', 'job overview'
            ]):
                in_description = True
                continue
            
            # Check if we're leaving description section
            if in_description and any(keyword in line_lower for keyword in [
                'requirements', 'responsibilities', 'qualifications', 'skills'
            ]):
                break
            
            if in_description and line.strip():
                description_lines.append(line.strip())
        
        return '\n'.join(description_lines) if description_lines else ""
    
    def _extract_requirements(self, text: str) -> List[str]:
        """Extract job requirements"""
        requirements = []
        lines = text.split('\n')
        in_requirements = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we're entering requirements section
            if any(keyword in line_lower for keyword in [
                'requirements', 'qualifications', 'what you need', 'must have'
            ]):
                in_requirements = True
                continue
            
            # Check if we're leaving requirements section
            if in_requirements and any(keyword in line_lower for keyword in [
                'responsibilities', 'duties', 'what you will do', 'benefits'
            ]):
                break
            
            if in_requirements and line.strip():
                # Clean up bullet points and numbering
                cleaned = re.sub(r'^[•\-\*\d\.\)]+\s*', '', line.strip())
                if cleaned and len(cleaned) > 10:
                    requirements.append(cleaned)
        
        return requirements
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities"""
        responsibilities = []
        lines = text.split('\n')
        in_responsibilities = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check if we're entering responsibilities section
            if any(keyword in line_lower for keyword in [
                'responsibilities', 'duties', 'what you will do', 'role responsibilities'
            ]):
                in_responsibilities = True
                continue
            
            # Check if we're leaving responsibilities section
            if in_responsibilities and any(keyword in line_lower for keyword in [
                'requirements', 'qualifications', 'skills', 'benefits'
            ]):
                break
            
            if in_responsibilities and line.strip():
                # Clean up bullet points and numbering
                cleaned = re.sub(r'^[•\-\*\d\.\)]+\s*', '', line.strip())
                if cleaned and len(cleaned) > 10:
                    responsibilities.append(cleaned)
        
        return responsibilities
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract required skills"""
        skills = []
        
        # Look for skills section
        lines = text.split('\n')
        in_skills = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in [
                'skills', 'technical skills', 'technologies', 'tools', 'technologies used'
            ]):
                in_skills = True
                continue
            
            if in_skills and any(keyword in line_lower for keyword in [
                'experience', 'education', 'benefits', 'about'
            ]):
                break
            
            if in_skills and line.strip():
                # Split by common delimiters
                line_skills = re.split(r'[,;•\n]', line)
                for skill in line_skills:
                    skill = skill.strip()
                    if skill and len(skill) > 2 and len(skill) < 50:
                        skills.append(skill)
        
        # Also extract skills from requirements
        if not skills:
            for req in self._extract_requirements(text):
                # Look for technical terms in requirements
                tech_skills = re.findall(r'\b(Python|Java|JavaScript|SQL|AWS|Azure|React|Angular|Node\.js|Docker|Kubernetes|Git|Agile|Scrum)\b', req, re.IGNORECASE)
                skills.extend(tech_skills)
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_experience_level(self, text: str) -> str:
        """Extract required experience level"""
        text_lower = text.lower()
        
        for level, keywords in self.experience_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level
        
        return ""
    
    def _extract_education_required(self, text: str) -> str:
        """Extract required education level"""
        text_lower = text.lower()
        
        for level, keywords in self.education_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level
        
        return ""
    
    def _extract_salary(self, text: str) -> str:
        """Extract salary information"""
        # Look for salary patterns
        salary_patterns = [
            r'\$(\d{1,3}(,\d{3})*\s*-\s*\d{1,3}(,\d{3})*)\s*(?:per\s*year|annually|annual)',
            r'\$(\d{1,3}(,\d{3})*)\s*-\s*\$(\d{1,3}(,\d{3})*)',
            r'(\d{1,3}(,\d{3})*)\s*-\s*(\d{1,3}(,\d{3})*)\s*(?:k|thousand)',
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group()
        
        return ""
    
    def _extract_job_type(self, text: str) -> str:
        """Extract job type"""
        text_lower = text.lower()
        
        job_types = {
            'full-time': ['full time', 'full-time', 'permanent'],
            'part-time': ['part time', 'part-time'],
            'contract': ['contract', 'contractor', 'temporary'],
            'remote': ['remote', 'work from home', 'wfh'],
            'hybrid': ['hybrid', 'mixed'],
            'onsite': ['onsite', 'on-site', 'in-office']
        }
        
        for job_type, keywords in job_types.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return job_type
        
        return ""
