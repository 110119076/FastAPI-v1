from fastapi import FastAPI, HTTPException, Path, Query
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

# @app.get("/patients/{patient_id}")
# def get_patient(patient_id: str):
#     data = load_data()
#     if patient_id in data:
#         return data[patient_id]
#     return {"error": "Patient not found"}


# Added Path parameter with description and example for better documentation in OpenAPI
# @app.get("/patients/{patient_id}")
# def get_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")):
#     data = load_data()
#     if patient_id in data:
#         return data[patient_id]
#     return {"error": "Patient not found"}



# Improved error handling by raising HTTPException with appropriate status code
@app.get("/patients/{patient_id}")
def get_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

@app.get("/sort")
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