from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import os
import tempfile
from pdfminer.high_level import extract_text
from processor import process_transcript
from dependencies import verify_api_key
import structlog
from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

load_dotenv()

app = FastAPI(
    title="Podcast Summary & Tag Generator",
    description="API for processing podcast transcripts",
    version="2.0",
    docs_url="/docs",
    redoc_url=None
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class TranscriptRequest(BaseModel):
    content: str
    language: str = "en"
    summary_length: int = 150

class TranscriptResponse(BaseModel):
    summary: str
    themes: List[str]
    tags: List[str]

# Helper Functions
def validate_file(file: UploadFile):
    """Simplified file validation without magic"""
    allowed_extensions = {'.txt', '.pdf'}
    max_size = 5 * 1024 * 1024  # 5MB
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, "Only .txt and .pdf files allowed")
    if file.size > max_size:
        raise HTTPException(413, "File too large (max 5MB)")

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Root route
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Routes
@app.post("/process")
async def process_text(
    request: Request,
    req: TranscriptRequest,
    #auth: bool = Depends(verify_api_key)
):
    """Process raw text"""
    try:
        result = process_transcript(
            req.content,
            req.language,
            req.summary_length
        )
        return result
    except Exception as e:
        # Check for Hugging Face quota error
        if hasattr(e, "response") and hasattr(e.response, "status_code") and e.response.status_code == 429:
            raise HTTPException(429, "Hugging Face API quota exceeded. Please check your plan and billing details.")
        if "insufficient_quota" in str(e) or "quota" in str(e).lower():
            raise HTTPException(429, "Hugging Face API quota exceeded. Please check your plan and billing details.")
        raise HTTPException(500, str(e))

@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("en"),
    summary_length: int = Form(150),
    auth: bool = Depends(verify_api_key)
):
    try:
        validate_file(file)
        
        if file.filename.endswith('.pdf'):
            with tempfile.NamedTemporaryFile(delete=False) as temp:
                temp.write(await file.read())
                content = extract_text(temp.name)
                os.unlink(temp.name)  # Clean up temp file
        else:
            content = (await file.read()).decode("utf-8")
        
        result = process_transcript(content, language, summary_length)
        return result
        
    except Exception as e:
        # Check for Hugging Face quota error
        if hasattr(e, "response") and hasattr(e.response, "status_code") and e.response.status_code == 429:
            raise HTTPException(429, "Hugging Face API quota exceeded. Please check your plan and billing details.")
        if "insufficient_quota" in str(e) or "quota" in str(e).lower():
            raise HTTPException(429, "Hugging Face API quota exceeded. Please check your plan and billing details.")
        raise HTTPException(500, str(e))

@app.post("/batch")
async def batch_process(
    files: List[UploadFile] = File(...),
    language: str = "en",
    summary_length: int = 150,
    auth: bool = Depends(verify_api_key)
):
    results = []
    for file in files:
        content = (await file.read()).decode("utf-8")
        result = process_transcript(content, language, summary_length)
        results.append({
            "filename": file.filename,
            **result
        })
    return results

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000))
    )
