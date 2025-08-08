from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field as ComputedField
from typing import Annotated, Literal, Optional
import json

app = FastAPI()


# ----------------------- MODELS ----------------------- #

class Patient(BaseModel):
    id: Annotated[int, Field(..., title="Patient ID", description="The ID of the patient")]
    name: Annotated[str, Field(..., title="Patient Name", description="The name of the patient")]
    city: Annotated[str, Field(..., title="Patient City", description="The city where the patient resides")]
    age: Annotated[int, Field(..., title="Patient Age", description="The age of the patient")]
    gender: Annotated[Literal['male', 'female', 'other'], Field(..., description="Gender of patient")]
    height: Annotated[float, Field(..., gt=0, title="Patient Height", description="Height in cm")]
    weight: Annotated[float, Field(..., gt=0, title="Patient Weight", description="Weight in kg")]

    @ComputedField
    @property
    def bmi(self) -> float:
        bmi = self.weight / ((self.height / 100) ** 2)
        return round(bmi, 2)

    @ComputedField
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "normal"
        elif 25 <= self.bmi < 29.9:
            return "overweight"
        else:
            return "obese"


class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female', 'other']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


# ----------------------- DATA UTILS ----------------------- #

def load_data():
    try:
        with open("patient.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # return empty list if file doesn't exist


def save_data(data):
    with open("patient.json", "w") as f:
        json.dump(data, f, indent=4)


# ----------------------- ROUTES ----------------------- #

@app.get("/")
def home():
    return {"message": "Patient Management System API"}


@app.get("/about")
def about():
    return {"message": "Fully functional API to manage patient records"}


@app.get("/view")
def view_all():
    return load_data()


@app.get("/patient/{id}")
def view_patient(id: int = Path(..., title="Patient ID")):
    data = load_data()
    for patient in data:
        if patient["id"] == id:
            return patient
    raise HTTPException(status_code=404, detail="Patient not found")


 #by height-http://127.0.0.1:8000/sort?sort_by=height&order=asc 
 #by name-http://127.0.0.1:8000/sort?sort_by=name&order=desc 
 #by id-http://127.0.0.1:8000/sort?sort_by=id&order=asc

@app.get("/sort")  

def sort_patients(
    sort_by: str = Query(..., title="Sort By", description="Sort by 'height', 'name', or 'id'"),
    order: str = Query("asc", title="Order", description="Sort order: 'asc' or 'desc'")
):
    valid_fields = ["height", "name", "id"]
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Choose from {valid_fields}")
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail="Invalid order. Use 'asc' or 'desc'")

    data = load_data()
    reverse = (order == "desc")
    return sorted(data, key=lambda x: x.get(sort_by, 0), reverse=reverse)


@app.post("/create")
def create_patient(patient: Patient):
    data = load_data()
    if any(p["id"] == patient.id for p in data):
        raise HTTPException(status_code=400, detail="Patient with this ID already exists")
    data.append(patient.model_dump())
    save_data(data)
    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})


@app.put("/edit/{patient_id}")
def update_patient(patient_id: int, patient_update: PatientUpdate):
    data = load_data()

    for index, patient in enumerate(data):
        if patient["id"] == patient_id:
            updated_info = patient_update.model_dump(exclude_unset=True)
            data[index].update(updated_info)

            # Validate and recompute BMI & verdict
            validated = Patient(**data[index])
            data[index] = validated.model_dump()

            save_data(data)
            return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})

    raise HTTPException(status_code=404, detail="Patient not found")
