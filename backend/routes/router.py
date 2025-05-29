# API endpoints for FastAPI
from fastapi import APIRouter
from llm.llm_manager import LLMManager


api_router = APIRouter()

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