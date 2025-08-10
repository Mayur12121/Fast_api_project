from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field,field_validator
from typing import Literal
import pickle
import pandas as pd

# Load the model
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

MODEL_VERSION='1.0.0'

app = FastAPI()

tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Pune", "Kolkata", "Hyderabad"]
tier_2_cities = [
    "Ahmedabad", "Jaipur", "Lucknow", "Kanpur", "Nagpur", "Indore", "Coimbatore",
    "Patna", "Bhopal", "Vadodara", "Visakhapatnam", "Surat", "Rajkot", "Agra",
    "Meerut", "Thane", "Nashik", "Vijayawada", "Aurangabad", "Madurai", "Jodhpur",
    "Amritsar", "Allahabad", "Varanasi", "Srinagar", "Gwalior", "Raipur", "Ranchi",
    "Dehradun", "Mysore", "Jamshedpur", "Udaipur", "Solapur", "Dhanbad", "Asansol",
    "Nanded", "Ajmer", "Bhilai", "Bikaner", "Guwahati", "Faridabad", "Kalyan",
    "Vasai-Virar", "Siliguri", "Jalandhar", "Ulhasnagar", "Bhubaneswar", "Warangal",
    "Nellore", "Guntur", "Amravati", "Cuttack", "Kochi", "Thiruvananthapuram",
    "Mangalore", "Jammu", "Raigarh", "Durgapur", "Bardhaman", "Kota", "Bilaspur",
    "Shimla", "Rourkela", "Kakinada", "Tiruchirappalli", "Ujjain", "Sagar", "Jhansi",
    "Gaya", "Bareilly", "Moradabad", "Aligarh", "Bhatinda", "Tirupati", "Nizamabad",
    "Kurnool", "Chandrapur", "Bhilwara", "Buxar", "Hapur", "Saharanpur",
    "Muzaffarpur", "Bardoli", "Kharagpur", "Shillong"
]

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

#home endpoint
@app.get('/')
def home():
    return{'home':"Insurance prediction api"}

#healthcheck endpoint
@app.get('/health')
def health_check():
    return{
        'status':'OK',
        'version':MODEL_VERSION
    }

@app.post("/predict")
def predict_premium(data: UserInput):
    input_df = pd.DataFrame([{
        'bmi': data.bmi,
        'age_group': data.age_group,
        'city_tier': data.city_tier,
        'income_lpa': data.income_lpa,
        'occupation': data.occupation,
        'lifestyle_risk':data.lifestyle_risk
    }])

    prediction = model.predict(input_df)[0]
    return JSONResponse(status_code=200, content={'predicted_category': prediction})
