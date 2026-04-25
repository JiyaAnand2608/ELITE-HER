import os
import uuid
import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from dotenv import load_dotenv

from models import Base, Session as SessionModel, Fragment as FragmentModel
from ai_service import analyze_fragment, structure_account
from pdf_service import generate_pdf

load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./fragment_first.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fragment First API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve PDF reports
os.makedirs("reports", exist_ok=True)
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class FragmentCreate(BaseModel):
    session_id: str
    content: str
    sensory_tags: Optional[str] = None

class FragmentResponse(BaseModel):
    id: int
    session_id: str
    content: str
    tagged_time: Optional[str]
    tagged_location: Optional[str]
    tagged_person: Optional[str]
    follow_up_question: Optional[str]

    class Config:
        from_attributes = True

@app.post("/sessions", response_model=dict)
def create_session(db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    db_session = SessionModel(id=session_id)
    db.add(db_session)
    db.commit()
    return {"session_id": session_id}

@app.post("/fragments", response_model=FragmentResponse)
def add_fragment(fragment: FragmentCreate, db: Session = Depends(get_db)):
    # 1. Analyze with AI
    ai_data = analyze_fragment(fragment.content)
    
    # 2. Save to DB
    db_fragment = FragmentModel(
        session_id=fragment.session_id,
        content=fragment.content,
        sensory_tags=fragment.sensory_tags,
        tagged_time=ai_data.get("time"),
        tagged_location=ai_data.get("location"),
        tagged_person=ai_data.get("person"),
        follow_up_question=ai_data.get("follow_up")
    )
    db.add(db_fragment)
    db.commit()
    db.refresh(db_fragment)
    return db_fragment

@app.get("/sessions/{session_id}/fragments", response_model=List[FragmentResponse])
def get_fragments(session_id: str, db: Session = Depends(get_db)):
    fragments = db.query(FragmentModel).filter(FragmentModel.session_id == session_id).all()
    return fragments

@app.post("/sessions/{session_id}/generate-pdf")
def export_pdf(session_id: str, db: Session = Depends(get_db)):
    fragments = db.query(FragmentModel).filter(FragmentModel.session_id == session_id).all()
    if not fragments:
        raise HTTPException(status_code=404, detail="No fragments found for this session")
    
    content_list = [f.content for f in fragments]
    structured_content = structure_account(content_list)
    
    pdf_filename = f"reports/account_{session_id}.pdf"
    os.makedirs("reports", exist_ok=True)
    
    generate_pdf(structured_content, pdf_filename)
    
    return {"pdf_url": f"/reports/account_{session_id}.pdf"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
