# API endpoints for FastAPI
from fastapi import APIRouter
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
    return get_user(user_id=user_id).get_response(prompt)

@api_router.get("/doctor_report/{user_id}")
def get_doctors_report(user_id: UUID, reason_for_visit: str):
    get_user(user_id=user_id).get_doctor_report(reason_for_visit)


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