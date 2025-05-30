# main.py
from fastapi import FastAPI
from app.routers import mock_sis_router, mock_lms_router, oneroster_router # Keep existing custom_router
# Import the new standard router
from app.routers.oneroster_router import oneroster_v1p1_router, custom_router # Import both routers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OneRoster PoC Backend",
    description="Backend for simulating source systems and processing OneRoster data, including standard v1.1 API.",
    version="0.3.0", # Increment version
)

# --- CORS Middleware (as before) ---
origins = [
    "http://localhost", "http://127.0.0.1",
    "http://localhost:8000", "http://localhost:8006", # Or your Uvicorn port
    "http://localhost:3000", "null",
]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
# --- End CORS Middleware ---

# Include mock system routers
app.include_router(mock_sis_router.router)
app.include_router(mock_lms_router.router)

# Include your custom combined data endpoint router
app.include_router(custom_router) # This was previously oneroster_router.router

# Include the new standard OneRoster v1.1 API router
app.include_router(oneroster_v1p1_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the OneRoster PoC Backend! Visit /docs for API details."}