from pydantic import BaseModel


class JobPostingInput(BaseModel):
    title: str = ""
    location: str = ""
    department: str = ""
    salary_range: str = ""
    company_profile: str = ""
    description: str = ""
    requirements: str = ""
    benefits: str = ""
    telecommuting: int = 0
    has_company_logo: int = 0
    has_questions: int = 0
    employment_type: str = ""
    required_experience: str = ""
    required_education: str = ""
    industry: str = ""
    function: str = ""


class PredictionResponse(BaseModel):
    is_fake: bool
    fake_probability: float
    trust_score: float
    risk_level: str
    indicators: list[str]
