from fastapi import APIRouter
from schemas import DashboardStats

router = APIRouter()

@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats():
    # Dummy data for now; replace with real DB/logic
    return DashboardStats(
        total_videos=10,
        total_documents=5,
        active_jobs=2,
        recent_uploads=[
            {"id": "1", "name": "Lecture 1", "type": "video", "created_at": "2025-10-01"},
            {"id": "2", "name": "Notes.pdf", "type": "document", "created_at": "2025-10-02"}
        ]
    )
