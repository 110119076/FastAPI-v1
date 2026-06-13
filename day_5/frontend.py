import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
api_url = os.getenv("API_URL")

st.title("Insurance Premium Prediction App")
st.markdown("Enter the details below to predict the insurance premium.")

# Input fields for user data
age = st.number_input("Age", min_value=1, max_value=120, value=30)
weight = st.number_input("Weight (kg)", min_value=1.0, value=65.0)
height = st.number_input("Height (m)", min_value=0.5, max_value=2.5, value=1.7)
income_lpa = st.number_input("Annual Income (LPA)", min_value=0.1, value=10.0)
smoker = st.selectbox("Smoker?", options=[True, False])
city = st.selectbox("City", options=['Jaipur', 'Chennai', 'Indore', 'Mumbai', 'Kota', 'Hyderabad',
       'Delhi', 'Chandigarh', 'Pune', 'Kolkata', 'Lucknow', 'Gaya',
       'Jalandhar', 'Mysore', 'Bangalore'])
occupation = st.selectbox("Occupation", options=['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'])

if st.button("Predict Premium"):
    input_data = {
        "age": age,
        "weight": weight,
        "height": height,
        "income_lpa": income_lpa,
        "smoker": smoker,
        "city": city,
        "occupation": occupation
    }

    try:
        response = requests.post(api_url, json=input_data)
        result = response.json()
        if response.status_code == 200:
            st.success(f"Predicted Insurance Premium: {result['predicted_category']}")
        else:
            st.error(f"Error: {result.get('detail', 'Unknown error occurred')}")
            st.write(result)
    
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to the FastAPI server. Please check if the backend server is running.")