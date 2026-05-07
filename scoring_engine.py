from typing import Dict, List, Any, Set
from dataclasses import dataclass
import re
from config import Config
from resume_parser import ResumeData
from job_parser import JobData

@dataclass
class ScoringResult:
    """Data class to store scoring results"""
    skills_score: float
    experience_score: float
    education_score: float
    certifications_score: float
    overall_score: float
    skills_details: Dict[str, Any]
    experience_details: Dict[str, Any]
    education_details: Dict[str, Any]
    certifications_details: Dict[str, Any]
    eligibility_status: str
    confidence_level: float

class ScoringEngine:
    """Advanced scoring engine for resume-job matching"""
    
    def __init__(self):
        self.config = Config()
        
        # Technical skill categories and weights
        self.skill_categories = {
            'programming_languages': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'web_technologies': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'spring'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite'],
            'cloud_platforms': ['aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean'],
            'devops_tools': ['docker', 'kubernetes', 'jenkins', 'gitlab', 'terraform', 'ansible', 'ci/cd'],
            'data_science': ['machine learning', 'data analysis', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn'],
            'mobile_development': ['ios', 'android', 'react native', 'flutter', 'swift', 'kotlin'],
            'other_tools': ['git', 'jira', 'slack', 'agile', 'scrum', 'tdd', 'microservices']
        }
        
        # Experience level mappings
        self.experience_levels = {
            'entry': {'min_years': 0, 'max_years': 2, 'weight': 0.8},
            'mid': {'min_years': 2, 'max_years': 5, 'weight': 1.0},
            'senior': {'min_years': 5, 'max_years': 10, 'weight': 1.2},
            'executive': {'min_years': 10, 'max_years': 50, 'weight': 1.5}
        }
        
        # Education level weights
        self.education_weights = {
            'high_school': 0.5,
            'bachelor': 1.0,
            'master': 1.3,
            'phd': 1.5
        }
    
    def calculate_match_score(self, resume_data: ResumeData, job_data: JobData) -> ScoringResult:
        """Calculate comprehensive match score between resume and job"""
        
        # Calculate individual scores
        skills_result = self._calculate_skills_score(resume_data, job_data)
        experience_result = self._calculate_experience_score(resume_data, job_data)
        education_result = self._calculate_education_score(resume_data, job_data)
        certifications_result = self._calculate_certifications_score(resume_data, job_data)
        
        # Calculate weighted overall score
        overall_score = (
            skills_result['score'] * self.config.SKILLS_WEIGHT +
            experience_result['score'] * self.config.EXPERIENCE_WEIGHT +
            education_result['score'] * self.config.EDUCATION_WEIGHT +
            certifications_result['score'] * self.config.CERTIFICATIONS_WEIGHT
        )
        
        # Determine eligibility status
        eligibility_status = self._determine_eligibility_status(overall_score, skills_result, experience_result)
        
        # Calculate confidence level
        confidence_level = self._calculate_confidence_level(
            skills_result, experience_result, education_result, certifications_result
        )
        
        return ScoringResult(
            skills_score=skills_result['score'],
            experience_score=experience_result['score'],
            education_score=education_result['score'],
            certifications_score=certifications_result['score'],
            overall_score=overall_score,
            skills_details=skills_result,
            experience_details=experience_result,
            education_details=education_result,
            certifications_details=certifications_result,
            eligibility_status=eligibility_status,
            confidence_level=confidence_level
        )
    
    def _calculate_skills_score(self, resume_data: ResumeData, job_data: JobData) -> Dict[str, Any]:
        """Calculate skills matching score"""
        
        resume_skills = set([skill.lower().strip() for skill in resume_data.skills])
        job_skills = set([skill.lower().strip() for skill in job_data.skills_required])
        
        # Direct skill matches
        direct_matches = resume_skills.intersection(job_skills)
        direct_match_score = len(direct_matches) / len(job_skills) if job_skills else 0
        
        # Semantic skill matching (using synonyms and related terms)
        semantic_matches = self._find_semantic_skill_matches(resume_skills, job_skills)
        semantic_match_score = len(semantic_matches) / len(job_skills) if job_skills else 0
        
        # Category-based scoring
        category_scores = self._calculate_category_scores(resume_skills, job_skills)
        
        # Final skills score (combination of direct and semantic matches)
        final_score = min(1.0, (direct_match_score * 0.7 + semantic_match_score * 0.3))
        
        return {
            'score': final_score * 100,
            'direct_matches': list(direct_matches),
            'semantic_matches': list(semantic_matches),
            'missing_skills': list(job_skills - resume_skills - semantic_matches),
            'category_scores': category_scores,
            'total_resume_skills': len(resume_skills),
            'total_job_skills': len(job_skills)
        }
    
    def _calculate_experience_score(self, resume_data: ResumeData, job_data: JobData) -> Dict[str, Any]:
        """Calculate experience matching score"""
        
        # Extract years of experience from resume
        resume_years = self._extract_years_of_experience(resume_data)
        
        # Get required experience level from job
        required_level = job_data.experience_level.lower() if job_data.experience_level else 'mid'
        
        # Calculate experience match
        if required_level in self.experience_levels:
            level_config = self.experience_levels[required_level]
            
            if resume_years >= level_config['min_years']:
                if resume_years <= level_config['max_years']:
                    experience_score = 100
                else:
                    # Overqualified - still good but not perfect match
                    experience_score = 85
            else:
                # Underqualified - calculate based on how close they are
                experience_score = (resume_years / level_config['min_years']) * 100 if level_config['min_years'] > 0 else 0
        else:
            # Default scoring if level not recognized
            experience_score = min(100, (resume_years / 5) * 100)
        
        # Analyze experience relevance
        relevance_score = self._calculate_experience_relevance(resume_data, job_data)
        
        # Final experience score combines years and relevance
        final_score = (experience_score * 0.6 + relevance_score * 0.4)
        
        return {
            'score': final_score,
            'years_of_experience': resume_years,
            'required_level': required_level,
            'relevance_score': relevance_score,
            'experience_level_match': self._get_experience_level_match(resume_years, required_level)
        }
    
    def _calculate_education_score(self, resume_data: ResumeData, job_data: JobData) -> Dict[str, Any]:
        """Calculate education matching score"""
        
        # Get highest education level from resume
        resume_education_level = self._get_highest_education_level(resume_data)
        
        # Get required education level from job
        required_education = job_data.education_required.lower() if job_data.education_required else 'bachelor'
        
        # Calculate education match
        if resume_education_level in self.education_weights and required_education in self.education_weights:
            resume_weight = self.education_weights[resume_education_level]
            required_weight = self.education_weights[required_education]
            
            if resume_weight >= required_weight:
                education_score = 100
            else:
                education_score = (resume_weight / required_weight) * 100
        else:
            education_score = 50  # Default if levels not recognized
        
        # Check for relevant field of study
        field_match_score = self._calculate_field_of_study_match(resume_data, job_data)
        
        # Final education score
        final_score = (education_score * 0.7 + field_match_score * 0.3)
        
        return {
            'score': final_score,
            'resume_education_level': resume_education_level,
            'required_education_level': required_education,
            'field_match_score': field_match_score,
            'education_meets_requirement': resume_weight >= required_weight if resume_education_level in self.education_weights and required_education in self.education_weights else False
        }
    
    def _calculate_certifications_score(self, resume_data: ResumeData, job_data: JobData) -> Dict[str, Any]:
        """Calculate certifications matching score"""
        
        resume_certs = set([cert.lower().strip() for cert in resume_data.certifications])
        
        # Extract required certifications from job requirements
        required_certs = self._extract_required_certifications(job_data)
        
        if not required_certs:
            # No specific certifications required
            return {
                'score': 100,  # Full points if no specific requirements
                'matching_certs': [],
                'missing_certs': [],
                'total_resume_certs': len(resume_certs)
            }
        
        # Find matching certifications
        matching_certs = set()
        for req_cert in required_certs:
            for resume_cert in resume_certs:
                if self._certifications_match(resume_cert, req_cert):
                    matching_certs.add(req_cert)
                    break
        
        # Calculate score
        cert_score = (len(matching_certs) / len(required_certs)) * 100 if required_certs else 100
        
        return {
            'score': cert_score,
            'matching_certs': list(matching_certs),
            'missing_certs': list(required_certs - matching_certs),
            'total_resume_certs': len(resume_certs),
            'total_required_certs': len(required_certs)
        }
    
    def _find_semantic_skill_matches(self, resume_skills: Set[str], job_skills: Set[str]) -> Set[str]:
        """Find semantic matches between skills using synonyms and related terms"""
        
        semantic_matches = set()
        
        # Skill synonyms and related terms
        skill_synonyms = {
            'javascript': ['js', 'ecmascript', 'node.js', 'nodejs'],
            'python': ['python3', 'python 3'],
            'java': ['jvm', 'spring boot', 'spring framework'],
            'aws': ['amazon web services', 'ec2', 's3', 'lambda'],
            'react': ['reactjs', 'react.js'],
            'angular': ['angularjs', 'angular.js'],
            'sql': ['mysql', 'postgresql', 't-sql', 'pl/sql'],
            'git': ['github', 'gitlab', 'version control'],
            'docker': ['containers', 'containerization'],
            'kubernetes': ['k8s', 'kube'],
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'data analysis': ['analytics', 'data analytics']
        }
        
        for job_skill in job_skills:
            if job_skill in resume_skills:
                continue  # Already counted as direct match
            
            # Check if job skill has synonyms that match resume skills
            for skill, synonyms in skill_synonyms.items():
                if job_skill == skill.lower() or job_skill in [s.lower() for s in synonyms]:
                    for synonym in synonyms:
                        if synonym.lower() in resume_skills:
                            semantic_matches.add(job_skill)
                            break
        
        return semantic_matches
    
    def _calculate_category_scores(self, resume_skills: Set[str], job_skills: Set[str]) -> Dict[str, float]:
        """Calculate skill category matching scores"""
        
        category_scores = {}
        
        for category, category_skills in self.skill_categories.items():
            category_skills_lower = [skill.lower() for skill in category_skills]
            
            resume_category_skills = resume_skills.intersection(category_skills_lower)
            job_category_skills = job_skills.intersection(category_skills_lower)
            
            if job_category_skills:
                category_score = len(resume_category_skills.intersection(job_category_skills)) / len(job_category_skills)
                category_scores[category] = category_score * 100
            else:
                category_scores[category] = 0  # No skills from this category required
        
        return category_scores
    
    def _extract_years_of_experience(self, resume_data: ResumeData) -> float:
        """Extract total years of experience from resume"""
        
        total_years = 0
        current_year = 2024  # Update this dynamically if needed
        
        for exp in resume_data.experience:
            duration = exp.get('duration', '')
            
            # Try to extract years from duration string
            year_patterns = [
                r'(\d+)\s*years?',
                r'(\d+)\s*-\s*(\d+)',  # Year range
                r'(\d{4})\s*-\s*(\d{4})',  # Full year range
                r'(\d{4})\s*-\s*present',  # Ongoing position
            ]
            
            for pattern in year_patterns:
                match = re.search(pattern, duration.lower())
                if match:
                    if len(match.groups()) == 2:
                        start_year = int(match.group(1))
                        end_year = int(match.group(2)) if match.group(2).isdigit() else current_year
                        years = end_year - start_year
                        total_years += max(0, years)
                        break
                    else:
                        years = int(match.group(1))
                        total_years += years
                        break
        
        return total_years
    
    def _calculate_experience_relevance(self, resume_data: ResumeData, job_data: JobData) -> float:
        """Calculate relevance of experience to job requirements"""
        
        if not resume_data.experience or not job_data.description:
            return 50  # Default score
        
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_data.description + ' ' + ' '.join(job_data.responsibilities))
        
        relevance_score = 0
        total_exp_entries = len(resume_data.experience)
        
        for exp in resume_data.experience:
            exp_text = exp.get('description', '').lower()
            exp_keywords = self._extract_keywords(exp_text)
            
            # Calculate keyword overlap
            overlap = len(job_keywords.intersection(exp_keywords))
            relevance_score += (overlap / len(job_keywords)) * 100 if job_keywords else 0
        
        return relevance_score / total_exp_entries if total_exp_entries > 0 else 0
    
    def _get_experience_level_match(self, resume_years: float, required_level: str) -> str:
        """Get experience level match description"""
        
        if required_level in self.experience_levels:
            level_config = self.experience_levels[required_level]
            
            if resume_years >= level_config['min_years']:
                if resume_years <= level_config['max_years']:
                    return "Perfect match"
                else:
                    return "Overqualified but suitable"
            else:
                return "Underqualified"
        
        return "Unknown"
    
    def _get_highest_education_level(self, resume_data: ResumeData) -> str:
        """Determine highest education level from resume"""
        
        education_levels = []
        
        for edu in resume_data.education:
            description = edu.get('description', '').lower()
            
            if any(keyword in description for keyword in ['phd', 'doctorate', 'doctoral']):
                education_levels.append('phd')
            elif any(keyword in description for keyword in ['master', 'ms', 'ma', 'mba']):
                education_levels.append('master')
            elif any(keyword in description for keyword in ['bachelor', 'bs', 'ba', 'undergraduate']):
                education_levels.append('bachelor')
            elif any(keyword in description for keyword in ['associate', 'diploma']):
                education_levels.append('high_school')
        
        # Return highest level found
        if 'phd' in education_levels:
            return 'phd'
        elif 'master' in education_levels:
            return 'master'
        elif 'bachelor' in education_levels:
            return 'bachelor'
        elif 'high_school' in education_levels:
            return 'high_school'
        else:
            return 'unknown'
    
    def _calculate_field_of_study_match(self, resume_data: ResumeData, job_data: JobData) -> float:
        """Calculate field of study relevance"""
        
        # Extract field of study from education
        resume_fields = set()
        for edu in resume_data.education:
            description = edu.get('description', '').lower()
            # Look for common field keywords
            fields = ['computer science', 'software engineering', 'information technology', 'data science', 'business', 'management']
            for field in fields:
                if field in description:
                    resume_fields.add(field)
        
        # Extract field requirements from job
        job_fields = set()
        job_text = (job_data.description + ' ' + ' '.join(job_data.requirements)).lower()
        for field in ['computer science', 'software engineering', 'information technology', 'data science', 'business', 'management']:
            if field in job_text:
                job_fields.add(field)
        
        if not job_fields:
            return 100  # No specific field required
        
        overlap = len(resume_fields.intersection(job_fields))
        return (overlap / len(job_fields)) * 100 if job_fields else 0
    
    def _extract_required_certifications(self, job_data: JobData) -> Set[str]:
        """Extract required certifications from job description"""
        
        required_certs = set()
        text = ' '.join(job_data.requirements + job_data.responsibilities).lower()
        
        # Common certification patterns
        cert_patterns = [
            r'(aws|azure|gcp)\s*(certified|certification)',
            r'(pmp|csm|cspo|csd|cssbb|cssgb)',
            r'(oracle|java|microsoft|cisco)\s*(certified|certification)',
            r'(certified)\s*(\w+\s*\w*)',  # Generic "certified X" pattern
        ]
        
        for pattern in cert_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    cert = ' '.join(match)
                else:
                    cert = match
                required_certs.add(cert.strip())
        
        return required_certs
    
    def _certifications_match(self, resume_cert: str, required_cert: str) -> bool:
        """Check if resume certification matches required certification"""
        
        # Direct match
        if resume_cert == required_cert:
            return True
        
        # Check if required cert is contained in resume cert or vice versa
        if required_cert in resume_cert or resume_cert in required_cert:
            return True
        
        # Check for common variations
        cert_variations = {
            'aws': ['amazon web services', 'aws certified'],
            'azure': ['microsoft azure', 'azure certified'],
            'pmp': ['project management professional'],
            'csm': ['certified scrummaster'],
        }
        
        for base, variations in cert_variations.items():
            if base in required_cert.lower():
                for variation in variations:
                    if variation in resume_cert.lower():
                        return True
        
        return False
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text"""
        
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        keywords = {word for word in words if len(word) > 2 and word not in stop_words}
        return keywords
    
    def _determine_eligibility_status(self, overall_score: float, skills_result: Dict, experience_result: Dict) -> str:
        """Determine final eligibility status"""
        
        # Check for critical gaps
        critical_skill_gap = len(skills_result.get('missing_skills', [])) > len(skills_result.get('direct_matches', []))
        critical_experience_gap = experience_result.get('years_of_experience', 0) < 1 and experience_result.get('required_level') in ['mid', 'senior', 'executive']
        
        # Determine status based on score and critical gaps
        if overall_score >= self.config.ELIGIBILITY_THRESHOLD * 100 and not critical_skill_gap and not critical_experience_gap:
            return "ELIGIBLE"
        elif overall_score >= 50 and not (critical_skill_gap and critical_experience_gap):
            return "MAYBE ELIGIBLE"
        else:
            return "NOT ELIGIBLE"
    
    def _calculate_confidence_level(self, skills_result: Dict, experience_result: Dict, education_result: Dict, certifications_result: Dict) -> float:
        """Calculate confidence level in the assessment"""
        
        # Base confidence on data completeness
        data_completeness = 0
        if skills_result.get('total_job_skills', 0) > 0:
            data_completeness += 0.3
        if experience_result.get('required_level'):
            data_completeness += 0.3
        if education_result.get('required_education_level'):
            data_completeness += 0.2
        if certifications_result.get('total_required_certs', 0) > 0:
            data_completeness += 0.2
        
        # Adjust confidence based on score consistency
        scores = [
            skills_result.get('score', 0),
            experience_result.get('score', 0),
            education_result.get('score', 0),
            certifications_result.get('score', 0)
        ]
        
        score_variance = max(scores) - min(scores)
        consistency_factor = max(0, 1 - (score_variance / 100))
        
        # Final confidence calculation
        confidence = (data_completeness * 0.6 + consistency_factor * 0.4) * 100
        
        return min(100, max(0, confidence))
