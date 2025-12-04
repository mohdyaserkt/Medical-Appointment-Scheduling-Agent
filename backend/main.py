from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api import chat, calendly_integration
from dotenv import load_dotenv
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):

    load_dotenv()
    # Startup
    print("Starting Medical Scheduling Agent...")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="Medical Appointment Scheduling Agent",
    description="AI-powered appointment scheduling system with Calendly integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(calendly_integration.router, prefix="/api/v1", tags=["calendly"])

@app.get("/")
async def root():
    return {
        "message": "Medical Appointment Scheduling Agent API",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)