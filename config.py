import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration (Primary)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Azure OpenAI (DISABLED - Not Used)
    # AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    # AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    # AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
    
    # Scoring weights
    SKILLS_WEIGHT = 0.4
    EXPERIENCE_WEIGHT = 0.3
    EDUCATION_WEIGHT = 0.2
    CERTIFICATIONS_WEIGHT = 0.1
    
    # Minimum eligibility threshold
    ELIGIBILITY_THRESHOLD = 0.7
