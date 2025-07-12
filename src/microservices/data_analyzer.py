from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Data Analyzer", description="Microservice for data analysis")

class AnalysisRequest(BaseModel):
    data: str
    analysis_type: str = "general"

class AnalysisResponse(BaseModel):
    result: str
    confidence: float
    analysis_type: str

@app.get("/")
async def root():
    return {"message": "Data Analyzer Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "data_analyzer"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest):
    try:
        # Basic analysis logic
        if not request.data:
            raise HTTPException(status_code=400, detail="Data cannot be empty")
        
        # Simple analysis based on data length
        data_length = len(request.data)
        confidence = min(0.95, data_length / 1000)  # Simple confidence calculation
        
        result = f"Analyzed {data_length} characters of {request.analysis_type} data"
        
        return AnalysisResponse(
            result=result,
            confidence=confidence,
            analysis_type=request.analysis_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)