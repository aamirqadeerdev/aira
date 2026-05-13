from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

# ── AIRA MAIN APPLICATION ──

app = FastAPI(
    title       = "AIRA — Agentic Identity & Risk Administration",
    description = "One Platform. Every Identity. Zero Risk.",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── REGISTER ALL ROUTES ──
from api.routes.auth_routes       import router as auth_router
from api.routes.identity_routes   import router as identity_router
from api.routes.agent_routes      import router as agent_router
from api.routes.compliance_routes import router as compliance_router

app.include_router(auth_router)
app.include_router(identity_router)
app.include_router(agent_router)
app.include_router(compliance_router)

# ── STARTUP EVENT ──
@app.on_event("startup")
async def startup_event():
    """Initialise AIRA on startup."""
    print("AIRA starting up...")

    # Initialise database
    try:
        from database.database_connection import init_database
        init_database()
        print("Database ready.")
    except Exception as e:
        print(f"Database init warning: {e}")

    # Seed ChromaDB with sample data
    try:
        from database.chromadb_store import chroma_store
        chroma_store.seed_sample_data()
        print("ChromaDB ready.")
    except Exception as e:
        print(f"ChromaDB init warning: {e}")

    print("AIRA is operational. One Platform. Every Identity. Zero Risk.")

# ── HEALTH ENDPOINTS ──
@app.get("/", tags=["Health"])
async def root():
    return {
        "product":    "AIRA",
        "tagline":    "One Platform. Every Identity. Zero Risk.",
        "version":    "1.0.0",
        "status":     "operational",
        "agents":     ["IGA", "PAM", "CIAM", "Frontline", "Machine", "Threat", "Compliance", "Remediation"],
        "sectors":    12,
        "frameworks": 14
    }

@app.get("/health", tags=["Health"])
async def health_check():
    try:
        from infrastructure.monitoring import monitor
        return monitor.check_system_health()
    except Exception:
        return {"status": "healthy", "api": "online"}

@app.get("/metrics", tags=["Health"])
async def get_metrics():
    try:
        from infrastructure.monitoring import monitor
        return monitor.get_dashboard_metrics()
    except Exception:
        return {"status": "metrics unavailable"}

# ── FRONTEND PAGE ROUTES ──
@app.get("/signin", tags=["Frontend"])
async def serve_signin():
    """Serve the AIRA Sign In page."""
    path = os.path.join("frontend", "signin.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"message": "Sign in page not found."}

@app.get("/dashboard", tags=["Frontend"])
async def serve_dashboard():
    """Serve the AIRA Control Centre dashboard."""
    path = os.path.join("frontend", "control_centre.html")
    if os.path.exists(path):
        return FileResponse(path)
    return {"message": "Dashboard not found."}

# ── SERVE FRONTEND STATIC FILES ──
# Must be mounted AFTER all routes
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host   = "0.0.0.0",
        port   = 8000,
        reload = True
    )
