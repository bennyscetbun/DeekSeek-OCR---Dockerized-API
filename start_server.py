#!/usr/bin/env python3
"""
DeepSeek-OCR vLLM Server
FastAPI wrapper for DeepSeek-OCR with vLLM backend
"""
from typing import List, Optional
from pydantic import BaseModel
import uvicorn
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from typing import Optional
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from server_commands import MODEL_PATH, initialize_model, llm, process_batch_endpoint, process_image_endpoint, process_pdf_endpoint


class OCRResponse(BaseModel):
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    page_count: Optional[int] = None

class BatchOCRResponse(BaseModel):
    success: bool
    results: List[OCRResponse]
    total_pages: int
    filename: str

# Initialize FastAPI app
app = FastAPI(
    title="DeepSeek-OCR API",
    description="High-performance OCR service using DeepSeek-OCR with vLLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    initialize_model()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "DeepSeek-OCR API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "model_loaded": llm is not None,
        "model_path": MODEL_PATH,
        "cuda_available": torch.cuda.is_available(),
        "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

@app.post("/ocr/image", response_model=OCRResponse)
async def server_process_image_endpoint(file: UploadFile = File(...), prompt: Optional[str] = Form(None)):
    try:
        print(f"[DEBUG] Image endpoint called for file: {file.filename}")
            
        # Read image data
        image_data = await file.read()
        print(f"[DEBUG] Read {len(image_data)} bytes of image data")
        ret = process_image_endpoint(image_data, prompt)
        return OCRResponse(
            success=ret.success,
            result=ret.result,
            error=ret.error,
            page_count=ret.page_count
        )
    except Exception as e:
        print(f"[ERROR] Image endpoint failed: {str(e)}")
        return OCRResponse(
            success=False,
            error=str(e)
        )`

@app.post("/ocr/pdf", response_model=BatchOCRResponse)
async def server_process_pdf_endpoint(file: UploadFile = File(...), prompt: Optional[str] = Form(None)):
    try:
        # Read PDF data
        print(f"[DEBUG] PDF endpoint called for file: {file.filename}")
        pdf_data = await file.read()
        print(f"[DEBUG] Read {len(pdf_data)} bytes of PDF data")
        ret = process_pdf_endpoint(pdf_data, prompt, file.filename)
        return BatchOCRResponse(
            success=ret.success,
            results=ret.results,
            total_pages=ret.total_pages,
            filename=file.filename
        )
    except Exception as e:
        print(f"[ERROR] PDF endpoint failed: {str(e)}")
        return BatchOCRResponse(
            success=False,
            results=[OCRResponse(success=False, error=str(e))],
            total_pages=0,
            filename=file.filename
        )

@app.post("/ocr/batch")
async def server_process_batch_endpoint(files: List[UploadFile] = File(...), prompt: Optional[str] = Form(None)):
    """Process multiple files (images and PDFs) with optional custom prompt"""
    results = []
    
    for file in files:
        if file.filename.lower().endswith('.pdf'):
            result = await server_process_pdf_endpoint(file, prompt)
        else:
            result = await server_process_image_endpoint(file, prompt)
        
        results.append({
            "filename": file.filename,
            "result": result
        })
    
    return {"success": True, "results": results}

if __name__ == "__main__":
    print("Starting DeepSeek-OCR API server...")
    uvicorn.run(
        "start_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )