import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

# Standardized imports assuming we run from the project root
try:
    from backend.recommender import get_search_engine
    from backend.summarizer import get_summarizer
    from backend.database import get_db, SavedPaper, SearchHistory
    from backend.trends import analyze_trends
except ImportError:
    # Fallback for local execution inside the backend folder
    from recommender import get_search_engine
    from summarizer import get_summarizer
    from database import get_db, SavedPaper, SearchHistory
    from trends import analyze_trends

app = FastAPI(title="PaperPilot API")

# Global Exception Handler
@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        import traceback
        print(f"🔥 GLOBAL CRASH: {e}")
        print(traceback.format_exc())
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e)}
        )

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your specific frontend URL
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

class SummaryResponse(BaseModel):
    summary: str

class InsightRequest(BaseModel):
    title: str
    abstract: str

class InsightResponse(BaseModel):
    methodology: Optional[str] = "Not specified"
    dataset: Optional[str] = "Not specified"
    key_results: Optional[str] = "Not specified"
    limitations: Optional[str] = "Not specified"
    future_work: Optional[str] = "Not specified"

class ChatRequest(BaseModel):
    title: str
    abstract: str
    question: str

class ChatResponse(BaseModel):
    answer: str

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
    return {"message": "PaperPilot API is running", "status": "online"}

@app.get("/health")
async def health():
    import time
    return {"status": "healthy", "timestamp": time.time()}

@app.post("/search", response_model=List[Paper])
async def search_papers(search_query: SearchQuery, db: Session = Depends(get_db)):
    try:
        # Record search history (silent failure if DB fails)
        try:
            history_entry = SearchHistory(query=search_query.query)
            db.add(history_entry)
            db.commit()
        except:
            db.rollback()
            
        engine = get_search_engine()
        results = engine.semantic_search(search_query.query, search_query.max_results)
        return results
    except Exception as e:
        print(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/recommend/{paper_id}")
async def recommend_papers(paper_id: str, title: str = "", abstract: str = ""):
    try:
        engine = get_search_engine()
        recommendations = engine.recommend_related_papers(paper_id, title, abstract)
        # Filter out the original paper
        recommendations = [p for p in recommendations if p['id'] != paper_id]
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize", response_model=SummaryResponse)
async def summarize_paper(request: SummaryRequest):
    try:
        s = get_summarizer()
        summary = s.summarize(request.text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-insights", response_model=InsightResponse)
async def extract_insights(request: InsightRequest):
    try:
        s = get_summarizer()
        insights = s.extract_insights(request.title, request.abstract)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_with_paper(request: ChatRequest):
    try:
        s = get_summarizer()
        answer = s.answer_question(request.title, request.abstract, request.question)
        return {"answer": answer}
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

@app.get("/citation-graph/{paper_id}")
async def get_citation_graph(paper_id: str, title: str = "", abstract: str = ""):
    try:
        engine = get_search_engine()
        graph_data = engine.get_citation_graph(paper_id, title=title, abstract=abstract)
        return graph_data
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
    import uvicorn
    # Read port from environment variable (provided by Railway)
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run("backend.app:app", host="0.0.0.0", port=port, reload=False)
