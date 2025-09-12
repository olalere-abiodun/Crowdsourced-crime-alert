from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.router import auth, crime
from .database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    create_db_and_tables()
    yield
    # Shutdown logic (if any)

# Create app with lifespan
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home():
    return {"message": "Welcome to Crowdsource Crime alert system"}

# Include routers

app.include_router(auth.router)
app.include_router(crime.router)


