# API endpoints for FastAPI
from http.client import HTTPException
from typing import List

import os

import db
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

from llm.llm_manager import LLMManager
from uuid import uuid4, UUID
from user.user import User



from db.db import Database
api_router = APIRouter()
users_dict = {}
class SignupData(BaseModel):
    mail: str
    age: int
    gender: str
    allergies: List[str]
    chronic_diseases: List[str]
    medications: List[str]

database = Database()




def get_user(user_id: UUID) -> User:

    if user_id in users_dict:
        return users_dict[user_id]
    new_user_id = UUID(os.getenv('UUID')) # for testing

    users_dict[new_user_id] = User(user_id=new_user_id, database=database)
    return users_dict[new_user_id]

    # new_user_id = uuid4()

@api_router.get("/signin_user/{user_email}")
def signin_user(user_email: str):
    """
    Signs in a user by email. If the user does not exist, it creates a new user.
    Returns the user_id.
    """
    try:
        patient = database.get_patient_by_email(user_email)
        user_id = UUID(patient['patient_id'])
        users_dict[user_id] = User(user_id=user_id, database=database)
    except Exception as e:
        # If the patient does not exist, create a new one
        print(f"Error fetching patient: {e}")

@api_router.get("/response/{user_id}")
def get_response(user_id: UUID, prompt: str):
    answer, stop = get_user(user_id=user_id).get_response(prompt)
    return JSONResponse(content={'answer': answer, 'stop': stop})


@api_router.post("/save_summary/{user_id}")
def save_summary(user_id: UUID):
    get_user(user_id=user_id).save_summary_and_update()
    return JSONResponse(content={'status': 'saved'})


@api_router.get("/doctor_report/{user_id}")
def get_doctors_report(user_id: UUID, prompt: str):
    answer = get_user(user_id=user_id).get_doctor_report(prompt)
    hpi_list  = answer['HPI'].split('\n')
    return JSONResponse(content={'reason': answer['reason'], 'HPI': hpi_list, 'impression': answer['impression']})


@api_router.get("/has_history/{user_id}")
def has_history(user_id: UUID) -> bool:
    """
    Checks if the user has any recorded symptoms in the database.
    Returns True if there are symptoms, False otherwise.
    """
    history = database.get_symptoms_for_patient(patient_id=user_id)
    return not len(history) == 0


@api_router.get("/get_history/{user_id}")
def get_history(user_id: UUID):
    """
    Checks if the user has any recorded symptoms in the database.
    Returns True if there are symptoms, False otherwise.
    """
    symptoms = database.get_symptoms_for_patient(patient_id=user_id)
    for symptom in symptoms:
        symptom['summary'] = symptom['summary'].split("\n")
    return JSONResponse(symptoms, status_code=200)


@api_router.get("/is_existing_patient/{email}")
def has_patient(email: str) -> bool:
    """
    Checks if a patient exists in the database by email.
    Returns True if the patient exists, False otherwise.
    """
    try:
        database.get_patient_by_email(email)
        return True
    except Exception as e:
        # If the patient does not exist, an exception will be raised
        return False
# consider maybe creating a function in the db for checking if a patient exists.

@api_router.post("/llm")
def llm_endpoint(input_data: dict):
    # Call LLM wrapper logic
    manager = LLMManager()
    result = manager.run(input_data)
    return {"result": result}
# example endpoint - post with path parameter (e.g., /submit/report/123) & query parameters


@api_router.post("/submit/report/{report_id}")
def submit_report(report_id: str, report_data: dict):
    # Logic to handle report submission
    # This could involve saving to a database or processing the report
    return {"report_id": report_id, "status": "submitted", "data": report_data}

@api_router.post("/auth/google")
def auth_google(token_data: str, age: int, gender: str, allergies: list = str, chronic_diseases: list = str, medications: list = str):
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token_data.token, grequests.Request(), "GOOGLE_CLIENT_ID"
        )

        # ID token is valid. Get user's Google Account info
        user_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name")
        try:
            database.get_patient(patient_id=user_id)
        except Exception as e:
            # If the patient does not exist, create a new one
            users_dict[user_id] = User(user_id=user_id, database=database)
            database.add_patient(patient_id=user_id,
                                 age=age,
                                 gender=gender,
                                 chronic_diseases=chronic_diseases,
                                 allergies=allergies,
                                 medications=medications)

        return {"email": email, "name": name, "user_id": user_id}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token")

@api_router.post("/auth/complete_signup")
def complete_signup(data: SignupData):
    # Might need to generate a uuid myself


    database.add_patient(age=data.age, gender=data.gender,
                         allergies=data.allergies, chronic_diseases=data.chronic_diseases,
                         medications=data.medications, patient_id=uuid4(), email=data.mail)

    # Return a simple confirmation response
    return {"message": "Signup data received successfully"}