from pydantic import BaseModel
from typing import List, Optional

class TranscriptRequest(BaseModel):
    content: str
    language: str = "en"
    summary_length: int = 150

class TranscriptResponse(BaseModel):
    summary: str
    themes: List[str]
    tags: List[str]

class BatchStatusResponse(BaseModel):
    task_id: str
    status: str
    processed: int
    total: int