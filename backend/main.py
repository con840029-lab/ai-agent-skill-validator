from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.database import Base, engine
from api import auth, skills
import os

app = FastAPI(
    title="AI Agent Skill Validator",
    description="Automated validation and evaluation platform for AI Agent Skills",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Create upload directory
os.makedirs("./uploads", exist_ok=True)

# Include routers
app.include_router(auth.router)
app.include_router(skills.router)


@app.get("/")
async def root():
    return {
        "name": "AI Agent Skill Validator",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth",
            "skills": "/api/skills"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
