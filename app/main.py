from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.logging_middleware import RequestLoggingMiddleware, configure_logging
from app.routers import auth, patients, doctors, appointments, records, analytics, dashboard

# Configure JSON / plain logging based on env (CloudWatch ingests JSON in Phase 2)
configure_logging()

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Cloud-Native Healthcare Data Management System",
    version="2.0.0",
)

# Per-request structured logging + X-Request-ID propagation
app.add_middleware(RequestLoggingMiddleware)

# CORS — allow all in dev, restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(records.router)
app.include_router(analytics.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME}
