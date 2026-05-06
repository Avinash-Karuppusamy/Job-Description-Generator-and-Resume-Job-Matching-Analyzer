from crewai import Crew
from agents import job_description_agent, quality_assurance_agent
from tasks import job_description_task, job_review_task

crew = Crew(
    agents=[job_description_agent, quality_assurance_agent],
    tasks=[job_description_task, job_review_task],
    verbose=True,
    memory=False
)

def run():
    job_role = input("Enter job role: ")

    inputs = {
        "job_role": job_role
    }

    result = crew.kickoff(inputs=inputs)

    print("\nGenerated Job Description:\n")
    print(result)

if __name__ == "__main__":
    run()