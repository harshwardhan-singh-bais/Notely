from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from database import Base

class Note(Base):
    __tablename__ = "notes"
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    source_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    model_used = Column(String)
    thumbnails = Column(Text)  # Comma-separated URLs
    markdown_url = Column(String)
    pdf_url = Column(String)

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    size = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String)
