from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Interactive Tool Generator Microservice")

class ToolRequest(BaseModel):
    description: str
    tool_type: str = "general"
    user_id: Optional[str] = None

class ToolResponse(BaseModel):
    tool_code: str
    tool_description: str
    status: str = "success"

@app.get("/")
async def root():
    return {"message": "Interactive Tool Generator Microservice is running"}

@app.post("/generate-tool", response_model=ToolResponse)
async def generate_tool(tool_request: ToolRequest):
    try:
        # Simular geração de ferramenta
        tool_code = f"""
# Ferramenta gerada para: {tool_request.description}
def generated_tool():
    print("Ferramenta gerada automaticamente")
    return "Ferramenta criada com sucesso"
        """
        
        return ToolResponse(
            tool_code=tool_code,
            tool_description=f"Ferramenta para: {tool_request.description}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tool: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "interactive_tool_generator"}