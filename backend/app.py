import os 

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.router import api_router

load_dotenv('../.env')
PORT = int(os.getenv("BACKEND_PORT", 8000))

app = FastAPI()
app.include_router(api_router, prefix="/api")

# Middleware for CORS - This allows the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development  # "http://localhost:5173
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Entry point for local dev
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=False, log_level="debug")
