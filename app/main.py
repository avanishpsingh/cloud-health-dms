from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.logging_middleware import RequestLoggingMiddleware, configure_logging
from app.routers import auth, patients, doctors, appointments, records, analytics, dashboard

try:
    from mangum import Mangum
except ImportError:  # pragma: no cover - local fallback before Phase 2 deps are installed
    Mangum = None

@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create tables automatically for local/demo environments.

    This keeps the assignment easy to run locally while still allowing stricter
    Phase 2 deployments to disable automatic schema creation.
    """
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Cloud-Native Healthcare Data Management System — Phase 1 (Local)",
    version="1.0.0",
    lifespan=lifespan,
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
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "deployment_target": settings.DEPLOYMENT_TARGET,
        "storage_mode": "s3" if settings.USE_S3_UPLOADS else "local",
    }


# AWS Lambda entrypoint for Phase 2.
# In the AWS console, the handler can be set to: app.main.handler
handler = Mangum(app) if Mangum else None
