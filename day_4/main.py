from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Patient Management System API!"}

@app.get("/about")
def about():
    return {"message": "To manage patient records"}

def load_data():
    with open("patients.json", "r") as f:
        return json.load(f)

@app.get("/patients")
def get_patients():
    data = load_data()
    return data

# Improved error handling by raising HTTPException with appropriate status code
@app.get("/patients/{patient_id}")
def get_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort")
# Note: The parameter ... inside Query indicates that this parameter is required
# Note: If the parameter ... is not used, then the parameter will be optional and will have a default value of None
def sort_patients(sort_by: str = Query(..., description="Sort on the basis of height, weight or bmi"),
                  order: str = Query("asc", description="Sort order: asc or desc")):
    data = load_data()
    valid_sort_by = ["height", "weight", "bmi"]
    if sort_by not in valid_sort_by:
        raise HTTPException(status_code=400, detail=f"Invalid value for sort_by, it should be within {valid_sort_by}")
    
    if order not in ["asc", "desc"]:
        raise HTTPException(status_code=400, detail=f"Invalid value for order, it should be within ['asc', 'desc']")

    sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=(order == "desc"))
    return sorted_data

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The unique ID of the patient", example="P001")]
    name: Annotated[str, Field(..., description="The name of the patient")]
    city: Annotated[str, Field(..., description="The city of the patient")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="The age of the patient")]
    gender: Annotated[Literal["male", "female", "others"], Field(..., description="The gender of the patient")]
    height: Annotated[float, Field(..., gt=0, description="The height of the patient in meters")]
    weight: Annotated[float, Field(..., gt=0, description="The weight of the patient in kilograms")]

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        bmi = self.bmi
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"


def save_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)


@app.post("/create")
def create_patient(patient: Patient):
    # load existing data
    data = load_data()

    # check if patient ID already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    
    # add new patient to data
    data[patient.id] = patient.model_dump(exclude=["id"])

    # save updated data back to file
    save_data(data)

    return JSONResponse(status_code=201, content={"message": "Patient created successfully"})

# PUT Method for Update

class PatientUpdate(BaseModel):
    id: Annotated[Optional[str], Field(default=None)]
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
    gender: Annotated[Optional[Literal["male", "female", "others"]], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]

@app.put("/update/{patient_id}")
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()

    # check if patient ID exists
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # update patient data
    existing_patient = data[patient_id]
    updated_patient = patient_update.model_dump(exclude_unset=True)
    
    for key, value in updated_patient.items():
        existing_patient[key] = value
    
    # existing_patient -> Patient pydantic obj -> bmi & verdict will be automatically computed -> convert back to dict and save in data
    existing_patient["id"] = patient_id  # add id back to the patient data
    updated_patient_obj = Patient(**existing_patient)
    data[patient_id] = updated_patient_obj.model_dump(exclude=["id"])

    # save updated data back to file
    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient updated successfully"})

@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = load_data()

    # check if patient ID exists
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # delete patient from data
    del data[patient_id]

    # save updated data back to file
    save_data(data)

    return JSONResponse(status_code=200, content={"message": "Patient deleted successfully"})