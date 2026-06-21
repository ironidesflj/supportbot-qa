"""FastAPI application entry point."""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
import uuid

from app.rag.ingestion import IngestionPipeline
from app.rag.retriever import Retriever
from app.rag.generator import Generator

app = FastAPI(title="SupportBot QA - Conversational AI Testing Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    query: str

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    answer: str
    sources: list[str]

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "SupportBot Backend"}

@app.post("/api/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Endpoint to upload and ingest documents into the knowledge base.
    
    Supported formats: .pdf, .txt, .md.
    """
    secure_filename = os.path.basename(file.filename)
    temp_file_path = f"temp_{uuid.uuid4()}_{secure_filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        pipeline = IngestionPipeline()
        chunks_count = pipeline.ingest(temp_file_path)
        
        return {
            "filename": file.filename,
            "status": "success",
            "chunks_added": chunks_count
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint utilizing the RAG pipeline.
    
    Processes a user query and returns an answer based on retrieved context.
    """
    try:
        retriever = Retriever()
        context, sources = retriever.retrieve_context(request.query)
        
        generator = Generator()
        answer = generator.generate_answer(request.query, context, sources)
        
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")
