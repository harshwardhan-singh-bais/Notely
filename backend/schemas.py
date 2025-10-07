from pydantic import BaseModel
from typing import List, Optional

class DashboardStats(BaseModel):
    total_videos: int
    total_documents: int
    active_jobs: int
    recent_uploads: List[dict]


class JobStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: Optional[int] = None
    message: Optional[str] = None


# Note schema for notes API
class Note(BaseModel):
    id: str
    title: str
    source_type: str  # video or document
    source_name: str
    created_at: str
    model_used: str
    thumbnails: List[str]
    markdown_url: Optional[str] = None
    pdf_url: Optional[str] = None


# Document metadata schema
class DocumentMeta(BaseModel):
    id: str
    name: str
    type: str
    size: int
    uploaded_at: str
    status: str  # pending, processed
