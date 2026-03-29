from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
import pandas as pd
from typing import List

from segmentation.segmenter import ContractSegmenter
from classification.risk_scorer import RiskScorer
from explanation.explainer import RiskExplainer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Legal Risk Suite API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Modules (Loaded once at startup)
segmenter = ContractSegmenter()
scorer = RiskScorer()
explainer = RiskExplainer()

class AnalysisRequest(BaseModel):
    text: str

class ExplanationRequest(BaseModel):
    clause: str
    risk_level: str

@app.post("/api/analyze")
async def analyze_contract(file: UploadFile = File(...)):
    """
    Uploads a contract file, segments it into clauses, and scores each clause for risk.
    """
    suffix = f".{file.filename.split('.')[-1]}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name

    try:
        text = segmenter.extract_text(tmp_path)
        clauses = segmenter.segment_into_clauses(text)
        
        results = []
        for i, clause in enumerate(clauses):
            score = scorer.score_clause(clause)
            results.append({
                "id": i + 1,
                "text": clause,
                "risk_level": score["risk_level"],
                "confidence": round(score['confidence'], 4),
                "method": score.get("method", "Inference")
            })
        
        # Calculate Summary Metrics
        total = len(results)
        high = len([r for r in results if r["risk_level"] == "High"])
        medium = len([r for r in results if r["risk_level"] == "Medium"])
        low = len([r for r in results if r["risk_level"] == "Low"])
        
        return {
            "filename": file.filename,
            "total_clauses": total,
            "risk_summary": {
                "high": high,
                "medium": medium,
                "low": low
            },
            "clauses": results,
            "full_text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@app.post("/api/explain")
async def explain_clause(request: ExplanationRequest):
    """
    Generates an AI-driven explanation for a specific flagged clause.
    """
    try:
        explanation = explainer.generate_explanation(request.clause, request.risk_level)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "model_loaded": scorer.model_loaded}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
