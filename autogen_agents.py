import autogen
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import json
from config import Config
from resume_parser import ResumeParser, ResumeData
from job_parser import JobParser, JobData

class ResumeJobMatchingAgents:
    """AutoGen agents for resume-job matching analysis"""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model or Config.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY in environment or config.")
        
        self.resume_parser = ResumeParser()
        self.job_parser = JobParser()
        
        # Initialize AutoGen agents
        self._setup_agents()
    
    def _setup_agents(self):
        """Setup AutoGen agents with specific roles"""
        
        # Configuration for LLM
        llm_config = {
            "config_list": [{
                "model": self.model,
                "api_key": self.api_key,
            }],
            "temperature": 0.1,
            "timeout": 60,
        }
        
        # Resume Analysis Agent
        self.resume_analyst = autogen.AssistantAgent(
            name="Resume_Analyst",
            system_message="""You are an expert Resume Analyst with deep expertise in evaluating resumes across various industries and roles.

Your responsibilities:
1. Analyze resume content and extract key qualifications, skills, and experiences
2. Identify strengths and weaknesses in the candidate's profile
3. Assess the candidate's experience level and career progression
4. Highlight relevant achievements and accomplishments
5. Provide objective evaluation of the candidate's qualifications

Focus on:
- Technical skills and competencies
- Years and relevance of experience
- Educational background and certifications
- Career progression and achievements
- Potential red flags or gaps

Be thorough, objective, and provide detailed analysis with specific examples from the resume.""",
            llm_config=llm_config
        )
        
        # Job Description Analyst
        self.job_analyst = autogen.AssistantAgent(
            name="Job_Analyst",
            system_message="""You are an expert Job Description Analyst with deep understanding of role requirements across different industries and seniority levels.

Your responsibilities:
1. Analyze job descriptions and extract key requirements and responsibilities
2. Identify mandatory vs. preferred qualifications
3. Assess the complexity and seniority level of the role
4. Determine critical skills and experiences needed
5. Provide insights into company culture and role expectations

Focus on:
- Technical and soft skills required
- Experience level and specific domain knowledge
- Educational and certification requirements
- Key responsibilities and deliverables
- Company-specific requirements or preferences

Be thorough and identify both explicit and implicit requirements.""",
            llm_config=llm_config
        )
        
        # Matching Specialist
        self.matching_specialist = autogen.AssistantAgent(
            name="Matching_Specialist",
            system_message="""You are an expert Resume-Job Matching Specialist with extensive experience in talent acquisition and candidate evaluation.

Your responsibilities:
1. Compare resume qualifications against job requirements
2. Calculate compatibility scores for different criteria (skills, experience, education, etc.)
3. Identify gaps between candidate profile and job requirements
4. Highlight strengths and potential concerns
5. Provide detailed matching analysis with specific recommendations

Scoring criteria:
- Skills Match: 40% weight
- Experience Match: 30% weight  
- Education Match: 20% weight
- Certifications: 10% weight

For each criterion, provide:
- Match score (0-100)
- Specific matching points
- Identified gaps
- Recommendations

Be objective, detailed, and provide actionable insights.""",
            llm_config=llm_config
        )
        
        # Eligibility Assessor
        self.eligibility_assessor = autogen.AssistantAgent(
            name="Eligibility_Assessor",
            system_message="""You are an expert Eligibility Assessor responsible for making final hiring recommendations based on comprehensive resume-job analysis.

Your responsibilities:
1. Review all analysis from other agents
2. Make final eligibility determination (Eligible/Not Eligible/Maybe Eligible)
3. Provide detailed justification for your decision
4. Identify potential interview questions or concerns
5. Suggest next steps in the hiring process

Eligibility criteria:
- Eligible: Overall score >= 70% with no critical gaps
- Maybe Eligible: Score 50-69% or some gaps that need clarification
- Not Eligible: Score < 50% or critical missing requirements

Provide:
- Final decision with confidence level
- Detailed justification
- Potential risks or concerns
- Recommended next steps
- Interview preparation suggestions

Be decisive but fair, and provide clear rationale for your recommendation.""",
            llm_config=llm_config
        )
        
        # Coordinator Agent
        self.coordinator = autogen.UserProxyAgent(
            name="Coordinator",
            system_message="""You are the Coordinator responsible for managing the resume-job matching process.

Your role:
1. Orchestrate the workflow between agents
2. Ensure all analysis is completed thoroughly
3. Compile final comprehensive report
4. Maintain quality and consistency across all analyses

Process:
1. Send resume to Resume_Analyst
2. Send job description to Job_Analyst  
3. Send both analyses to Matching_Specialist
4. Send matching analysis to Eligibility_Assessor
5. Compile final report

Ensure each agent provides detailed, structured analysis before proceeding to the next step.""",
            code_execution_config=False,
            human_input_mode="NEVER"
        )
    
    def analyze_resume_job_match(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Main method to analyze resume against job description"""
        
        # Parse resume and job description
        resume_data = self.resume_parser.parse_resume_text(resume_text)
        job_data = self.job_parser.parse_job(job_description)
        
        # Start the analysis workflow
        analysis_result = {
            "resume_data": asdict(resume_data),
            "job_data": asdict(job_data),
            "analysis": {},
            "final_recommendation": {}
        }
        
        # Step 1: Resume Analysis
        resume_analysis = self._get_resume_analysis(resume_data)
        analysis_result["analysis"]["resume_analysis"] = resume_analysis
        
        # Step 2: Job Analysis
        job_analysis = self._get_job_analysis(job_data)
        analysis_result["analysis"]["job_analysis"] = job_analysis
        
        # Step 3: Matching Analysis
        matching_analysis = self._get_matching_analysis(resume_analysis, job_analysis, resume_data, job_data)
        analysis_result["analysis"]["matching_analysis"] = matching_analysis
        
        # Step 4: Eligibility Assessment
        eligibility_assessment = self._get_eligibility_assessment(matching_analysis)
        analysis_result["final_recommendation"] = eligibility_assessment
        
        return analysis_result
    
    def _get_resume_analysis(self, resume_data: ResumeData) -> Dict[str, Any]:
        """Get resume analysis from Resume Analyst agent"""
        
        resume_text = f"""
        Resume Analysis Request:
        
        Name: {resume_data.name}
        Email: {resume_data.email}
        Phone: {resume_data.phone}
        Location: {resume_data.location}
        
        Summary:
        {resume_data.summary}
        
        Skills:
        {', '.join(resume_data.skills)}
        
        Experience:
        {self._format_experience(resume_data.experience)}
        
        Education:
        {self._format_education(resume_data.education)}
        
        Certifications:
        {', '.join(resume_data.certifications)}
        
        Please provide a comprehensive analysis of this resume, focusing on:
        1. Overall profile assessment
        2. Skills and competencies evaluation
        3. Experience level and relevance
        4. Educational background analysis
        5. Strengths and potential concerns
        6. Career progression assessment
        """
        
        # Create a temporary message handler
        class MessageHandler:
            def __init__(self):
                self.response = ""
            
            def receive(self, message, sender, request_reply=None):
                self.response = str(message)
        
        handler = MessageHandler()
        
        # Start the conversation
        self.coordinator.initiate_chat(
            self.resume_analyst,
            message=resume_text,
            max_turns=1
        )
        
        # Get the last message from the resume analyst
        messages = self.resume_analyst.chat_messages[self.coordinator]
        if messages:
            last_message = messages[-1]['content']
        else:
            last_message = "Resume analysis completed."
        
        return {
            "analysis": last_message,
            "structured_data": asdict(resume_data)
        }
    
    def _get_job_analysis(self, job_data: JobData) -> Dict[str, Any]:
        """Get job analysis from Job Analyst agent"""
        
        job_text = f"""
        Job Description Analysis Request:
        
        Title: {job_data.title}
        Company: {job_data.company}
        Location: {job_data.location}
        
        Description:
        {job_data.description}
        
        Requirements:
        {self._format_list(job_data.requirements)}
        
        Responsibilities:
        {self._format_list(job_data.responsibilities)}
        
        Skills Required:
        {', '.join(job_data.skills_required)}
        
        Experience Level: {job_data.experience_level}
        Education Required: {job_data.education_required}
        Salary: {job_data.salary}
        Job Type: {job_data.job_type}
        
        Please provide a comprehensive analysis of this job description, focusing on:
        1. Role complexity and seniority level
        2. Critical vs. preferred requirements
        3. Technical and soft skills needed
        4. Experience and education requirements
        5. Company culture indicators
        6. Potential challenges or expectations
        """
        
        # Start the conversation
        self.coordinator.initiate_chat(
            self.job_analyst,
            message=job_text,
            max_turns=1
        )
        
        # Get the last message from the job analyst
        messages = self.job_analyst.chat_messages[self.coordinator]
        if messages:
            last_message = messages[-1]['content']
        else:
            last_message = "Job analysis completed."
        
        return {
            "analysis": last_message,
            "structured_data": asdict(job_data)
        }
    
    def _get_matching_analysis(self, resume_analysis: Dict, job_analysis: Dict, 
                              resume_data: ResumeData, job_data: JobData) -> Dict[str, Any]:
        """Get matching analysis from Matching Specialist agent"""
        
        matching_text = f"""
        Resume-Job Matching Analysis Request:
        
        RESUME ANALYSIS:
        {resume_analysis['analysis']}
        
        JOB ANALYSIS:
        {job_analysis['analysis']}
        
        STRUCTURED DATA FOR COMPARISON:
        
        Resume Skills: {', '.join(resume_data.skills)}
        Job Required Skills: {', '.join(job_data.skills_required)}
        
        Resume Experience: {self._format_experience(resume_data.experience)}
        Job Experience Level: {job_data.experience_level}
        
        Resume Education: {self._format_education(resume_data.education)}
        Job Education Required: {job_data.education_required}
        
        Resume Certifications: {', '.join(resume_data.certifications)}
        
        Please provide a detailed matching analysis with:
        1. Skills match score (0-100) with breakdown
        2. Experience match score (0-100) with breakdown
        3. Education match score (0-100) with breakdown
        4. Certifications match score (0-100) with breakdown
        5. Overall compatibility score (weighted average)
        6. Identified gaps and concerns
        7. Strengths and matching points
        8. Specific recommendations
        
        Use the scoring weights:
        - Skills Match: 40%
        - Experience Match: 30%
        - Education Match: 20%
        - Certifications: 10%
        """
        
        # Start the conversation
        self.coordinator.initiate_chat(
            self.matching_specialist,
            message=matching_text,
            max_turns=1
        )
        
        # Get the last message from the matching specialist
        messages = self.matching_specialist.chat_messages[self.coordinator]
        if messages:
            last_message = messages[-1]['content']
        else:
            last_message = "Matching analysis completed."
        
        return {
            "analysis": last_message,
            "detailed_scores": self._extract_scores(last_message)
        }
    
    def _get_eligibility_assessment(self, matching_analysis: Dict) -> Dict[str, Any]:
        """Get final eligibility assessment from Eligibility Assessor agent"""
        
        eligibility_text = f"""
        Final Eligibility Assessment Request:
        
        MATCHING ANALYSIS:
        {matching_analysis['analysis']}
        
        DETAILED SCORES:
        {matching_analysis['detailed_scores']}
        
        Please provide the final eligibility assessment with:
        1. Final decision: ELIGIBLE / MAYBE ELIGIBLE / NOT ELIGIBLE
        2. Overall confidence level (0-100%)
        3. Detailed justification for the decision
        4. Key strengths that support the decision
        5. Critical concerns or gaps
        6. Recommended next steps
        7. Suggested interview questions or areas to explore
        8. Risk assessment for hiring this candidate
        
        Use these criteria:
        - Eligible: Overall score >= 70% with no critical gaps
        - Maybe Eligible: Score 50-69% or some gaps that need clarification
        - Not Eligible: Score < 50% or critical missing requirements
        """
        
        # Start the conversation
        self.coordinator.initiate_chat(
            self.eligibility_assessor,
            message=eligibility_text,
            max_turns=1
        )
        
        # Get the last message from the eligibility assessor
        messages = self.eligibility_assessor.chat_messages[self.coordinator]
        if messages:
            last_message = messages[-1]['content']
        else:
            last_message = "Eligibility assessment completed."
        
        return {
            "assessment": last_message,
            "decision": self._extract_decision(last_message),
            "confidence": self._extract_confidence(last_message)
        }
    
    def _format_experience(self, experience_list: List[Dict]) -> str:
        """Format experience list for display"""
        if not experience_list:
            return "No experience listed"
        
        formatted = []
        for exp in experience_list:
            formatted.append(f"- {exp.get('description', 'N/A')}")
        return '\n'.join(formatted)
    
    def _format_education(self, education_list: List[Dict]) -> str:
        """Format education list for display"""
        if not education_list:
            return "No education listed"
        
        formatted = []
        for edu in education_list:
            formatted.append(f"- {edu.get('description', 'N/A')}")
        return '\n'.join(formatted)
    
    def _format_list(self, items: List[str]) -> str:
        """Format list for display"""
        if not items:
            return "None listed"
        
        return '\n'.join([f"- {item}" for item in items])
    
    def _extract_scores(self, analysis_text: str) -> Dict[str, Any]:
        """Extract scores from analysis text"""
        scores = {}
        
        # Look for score patterns in the text
        import re
        
        # Extract individual scores
        score_patterns = [
            (r'skills.*?(\d+)', 'skills_score'),
            (r'experience.*?(\d+)', 'experience_score'),
            (r'education.*?(\d+)', 'education_score'),
            (r'certifications?.*?(\d+)', 'certifications_score'),
            (r'overall.*?(\d+)', 'overall_score')
        ]
        
        for pattern, key in score_patterns:
            match = re.search(pattern, analysis_text.lower())
            if match:
                scores[key] = int(match.group(1))
            else:
                scores[key] = 0
        
        return scores
    
    def _extract_decision(self, assessment_text: str) -> str:
        """Extract final decision from assessment text"""
        text_lower = assessment_text.lower()
        
        if 'eligible' in text_lower and 'not eligible' not in text_lower and 'maybe eligible' not in text_lower:
            return 'ELIGIBLE'
        elif 'maybe eligible' in text_lower or 'potentially eligible' in text_lower:
            return 'MAYBE ELIGIBLE'
        else:
            return 'NOT ELIGIBLE'
    
    def _extract_confidence(self, assessment_text: str) -> int:
        """Extract confidence level from assessment text"""
        import re
        
        # Look for confidence percentage
        match = re.search(r'confidence.*?(\d+)%', assessment_text.lower())
        if match:
            return int(match.group(1))
        
        # Default confidence based on decision
        decision = self._extract_decision(assessment_text)
        if decision == 'ELIGIBLE':
            return 80
        elif decision == 'MAYBE ELIGIBLE':
            return 60
        else:
            return 90
