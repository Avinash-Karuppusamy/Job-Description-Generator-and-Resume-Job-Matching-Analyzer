from crewai import Agent

# Job Description Generator Agent
job_description_agent = Agent(
    role="Job Description Generator",
    goal="Generate professional job descriptions based on job roles",
    backstory=(
        "You are an expert HR professional skilled in writing job descriptions "
        "including responsibilities, skills, and qualifications."
    ),
    verbose=True,
    llm="ollama/mistral"
)

# Quality Assurance Agent
quality_assurance_agent = Agent(
    role="Quality Assurance Specialist",
    goal="Review and improve job descriptions",
    backstory=(
        "You refine and improve job descriptions to ensure clarity and completeness."
    ),
    verbose=True,
    llm="ollama/mistral"
)