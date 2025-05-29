# API endpoints for FastAPI
from http.client import HTTPException

import db
from fastapi import APIRouter
from fastapi.responses import JSONResponse
# from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

from llm.llm_manager import LLMManager
from uuid import uuid4, UUID
from user.user import User



from db.db import Database
api_router = APIRouter()
users_dict = {}

database = Database()

def get_user(user_id: UUID) -> User:

    if user_id in users_dict:
        return users_dict[user_id]
    new_user_id = UUID("00000000-0000-0000-0000-000000000000") # for testing

    users_dict[new_user_id] = User(user_id=new_user_id, database=database)
    return users_dict[new_user_id]

    # new_user_id = uuid4()

@api_router.get("/response/{user_id}")
def get_response(user_id: UUID, prompt: str):
    # print("Received prompt:", prompt)
    answer = get_user(user_id=user_id).get_response(prompt)
    return JSONResponse(content={'answer': answer})


@api_router.post("/save_summary/{user_id}")
def save_summary(user_id: UUID):
    get_user(user_id=user_id).save_summary_and_update()
    return JSONResponse(content={'status': 'saved'})

@api_router.get("/doctor_report/{user_id}")
def get_doctors_report(user_id: UUID, prompt: str):
    print("Received prompt:", prompt)

    answer = get_user(user_id=user_id).get_doctor_report(prompt)
    return JSONResponse(content={'answer': answer})

@api_router.get("/has_history/{user_id}")
def has_history(user_id: UUID) -> bool:
    """
    Checks if the user has any recorded symptoms in the database.
    Returns True if there are symptoms, False otherwise.
    """
    history = database.get_symptoms_for_patient(patient_id=user_id)
    return not len(history) == 0

@api_router.get("/get_history/{user_id}")
def get_history(user_id: UUID) -> bool:
    """
    Checks if the user has any recorded symptoms in the database.
    Returns True if there are symptoms, False otherwise.
    """
    return database.get_symptoms_for_patient(patient_id=user_id)

# example endpoint -simple GET

@api_router.get("/status")
def status():
    return {"status": "ok"}
# example endpoint - GET with url parameter (e.g., /health/1)

@api_router.get("/health/{id}")
def get_health(id: int):
    return {"status": "healthy", "id": id}
# example endpoint - GET with query parameters (e.g., /get/report?report_id=123)


@api_router.get("/get/report")
def get_report(report_id: str):
    # Logic to retrieve a report based on the report_id
    # This could involve fetching from a database or other storage
    return {"report_id": report_id, "status": "retrieved"}
# example endpoint - simple POST, with JSON body

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