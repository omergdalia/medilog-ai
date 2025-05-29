from fastapi import FastAPI

from routes.router import api_router

app = FastAPI()

app.include_router(api_router, prefix="/api")

# Middleware for CORS - This allows the frontend to communicate with the backend
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Entry point for local dev
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
