
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dashboard import router as dashboard_router
from notes import router as notes_router
from documents import router as documents_router
from videos import router as videos_router
from settings import router as settings_router

app = FastAPI()

# CORS setup for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(notes_router)
app.include_router(documents_router)
app.include_router(videos_router)
app.include_router(settings_router)

@app.get("/health")
def health():
    return {"status": "ok"}


# Root endpoint for friendly message
@app.get("/")
def root():
    return {"message": "Notely backend is running"}
