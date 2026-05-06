from crewai import Task
from agents import job_description_agent, quality_assurance_agent

# Task 1: Generate Job Description
job_description_task = Task(
    description=(
        "The user provided a job role: {job_role}\n\n"
        "Generate a complete job description including:\n"
        "- Role summary\n"
        "- Responsibilities\n"
        "- Required skills\n"
        "- Qualifications\n"
        "- Tools/Technologies\n\n"
        "Make it professional and clear."
    ),
    expected_output="A structured job description.",
    agent=job_description_agent
)

# Task 2: Review and Improve
job_review_task = Task(
    description=(
        "Review the generated job description and improve clarity, completeness, and professionalism."
    ),
    expected_output="A refined and polished job description.",
    agent=quality_assurance_agent
)