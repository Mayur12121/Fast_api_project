from pydantic import BaseModel, Field, computed_field,field_validator
from typing import Literal
from config.city_tier import tier_1_cities,tier_2_cities

# Pydantic model to validate incoming data
class UserInput(BaseModel):
    age: int = Field(..., gt=0, description="Age of User")
    weight: float = Field(..., gt=0, description="Weight in kg")
    height: float = Field(..., gt=0, description="Height in meters")
    income_lpa: float = Field(..., gt=0, description="Income in lakhs per annum")
    smoker: Literal['yes', 'no'] = Field(..., description="Smoking status")
    city: str = Field(..., description="City of residence")
    occupation: Literal['retired', 'freelancer', 'student', 'government_job', 'private_job', 'unemployed', 'businessman'] = Field(..., description="Occupation type")
    
    @field_validator('city')
    @classmethod
    def normalize_city(cls,v:str)->str:
        v=v.strip().title()

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight / (self.height ** 2)

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker == 'yes' and self.bmi > 30:
            return "high"
        elif self.smoker == 'yes' or self.bmi > 27:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "middle-aged"
        elif self.age < 60:
            return "middle_aged"
        return "senior"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        if self.city in tier_2_cities:
            return 2
        return 3
