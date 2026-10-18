from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app_build.backend.config import settings
from app_build.backend.db import init_db
from app_build.backend.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables
    init_db()
    yield

app = FastAPI(
    title="NetMirage Defensive Cyber-Range Platform",
    description="Real-time defensive cyber-range platform with zero-egress sandboxing, passive protocol intelligence, MITRE ATT&CK mapping, and dynamic deception routing.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "name": "NetMirage Defensive Cyber-Range Platform",
        "status": "operational",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_build.backend.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
