from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import ping_database
from app.routers import auth, institutes, inspectors, assignments, reports, alerts, websocket

app = FastAPI(
    title="Nigrani Setu API",
    description="Backend for the DoSJE Real-Time Monitoring & Inspection platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves uploaded inspection photos at /uploads/<filename>
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(institutes.router)
app.include_router(inspectors.router)
app.include_router(assignments.router)
app.include_router(reports.router)
app.include_router(alerts.router)
app.include_router(websocket.router)


@app.on_event("startup")
async def startup_event():
    await ping_database()


@app.get("/")
async def root():
    return {"status": "ok", "service": "Nigrani Setu API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
