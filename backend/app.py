# FastAPI backend for the medical web app
# To run: pip install fastapi uvicorn

from fastapi import FastAPI

from router import api_router

app = FastAPI()

app.include_router(api_router, prefix="/api")

# Entry point for local dev
if __name__ == "__main__":
    import uvicorn
    # print("Starting FastAPI server on http://localhost:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000)
