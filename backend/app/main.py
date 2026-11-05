from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Automatically create database tables when the backend starts
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Mini Task Manager API",
    description="REST API for the Mini Task Manager mobile application using FastAPI, SQLAlchemy, and SQLite.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS to permit requests from Flutter mobile (physical device / emulator / web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register task endpoints
app.include_router(tasks.router)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Mini Task Manager Backend",
        "docs": "/docs"
    }

