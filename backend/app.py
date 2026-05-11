from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
try:
    from backend.recommender import get_search_engine
    from backend.summarizer import get_summarizer
    from backend.database import get_db, SavedPaper, SearchHistory
    from backend.trends import analyze_trends
except ImportError:
    from recommender import get_search_engine
    from summarizer import get_summarizer
    from database import get_db, SavedPaper, SearchHistory
    from trends import analyze_trends

from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import Depends
import uvicorn

app = FastAPI(title="PaperPilot API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SearchQuery(BaseModel):
    query: str
    max_results: Optional[int] = 10

class SummaryRequest(BaseModel):
    text: str

class Paper(BaseModel):
    id: str
    title: str
    abstract: str
    authors: List[str]
    published: str
    link: str
    relevance_score: Optional[float] = None

class SavedPaperSchema(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    link: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

@app.get("/")
async def root():
    return {"message": "PaperPilot API is running"}

@app.post("/search", response_model=List[Paper])
async def search_papers(search_query: SearchQuery, db: Session = Depends(get_db)):
    try:
        # Record search history
        history_entry = SearchHistory(query=search_query.query)
        db.add(history_entry)
        db.commit()
        
        engine = get_search_engine()
        results = engine.semantic_search(search_query.query, search_query.max_results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend/{paper_id}")
async def recommend_papers(paper_id: str, title: str = "", abstract: str = ""):
    try:
        engine = get_search_engine()
        # Use provided abstract/title if available, otherwise would need to fetch (omitted for speed)
        recommendations = engine.recommend_related_papers(paper_id, title, abstract)
        # Filter out the original paper from recommendations
        recommendations = [p for p in recommendations if p['id'] != paper_id]
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize")
async def summarize_paper(request: SummaryRequest):
    try:
        summarizer = get_summarizer()
        summary = summarizer.summarize(request.text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Reading List Endpoints
@app.post("/reading-list")
async def save_paper(paper: SavedPaperSchema, db: Session = Depends(get_db)):
    db_paper = SavedPaper(
        paper_id=paper.paper_id,
        title=paper.title,
        authors=", ".join(paper.authors),
        abstract=paper.abstract,
        link=paper.link,
        notes=paper.notes
    )
    db.add(db_paper)
    try:
        db.commit()
        db.refresh(db_paper)
        return db_paper
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Paper already in reading list")

@app.get("/reading-list")
async def get_reading_list(db: Session = Depends(get_db)):
    papers = db.query(SavedPaper).all()
    return papers

@app.delete("/reading-list/{paper_id}")
async def remove_from_reading_list(paper_id: str, db: Session = Depends(get_db)):
    paper = db.query(SavedPaper).filter(SavedPaper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    db.delete(paper)
    db.commit()
    return {"message": "Paper removed"}

@app.get("/trends/{topic}")
async def get_trends(topic: str):
    try:
        return analyze_trends(topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/citations/{paper_id}")
async def get_citations(paper_id: str, title: str = ""):
    try:
        engine = get_search_engine()
        return engine.fetch_citations(paper_id, title=title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_history(db: Session = Depends(get_db)):
    try:
        history = db.query(SearchHistory).order_by(desc(SearchHistory.timestamp)).limit(20).all()
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    # Detect if we are running inside the backend folder or at the root
    if os.path.exists("backend"):
        app_path = "backend.app:app"
    else:
        app_path = "app:app"
    
    print(f"Starting app on port {port} with entry point {app_path}")
    uvicorn.run(app_path, host="0.0.0.0", port=port, reload=False)
