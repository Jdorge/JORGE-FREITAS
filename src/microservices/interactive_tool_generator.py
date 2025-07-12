from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Interactive Tool Generator", description="Microservice for generating interactive tools")

class ToolRequest(BaseModel):
    tool_type: str
    description: str
    parameters: dict = {}

class ToolResponse(BaseModel):
    tool_id: str
    tool_type: str
    generated_code: str
    status: str

@app.get("/")
async def root():
    return {"message": "Interactive Tool Generator Service is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "interactive_tool_generator"}

@app.post("/generate", response_model=ToolResponse)
async def generate_tool(request: ToolRequest):
    try:
        if not request.tool_type or not request.description:
            raise HTTPException(status_code=400, detail="Tool type and description are required")
        
        # Generate a simple tool based on type
        tool_id = f"tool_{request.tool_type}_{len(request.description)}"
        
        # Simple code generation based on tool type
        if request.tool_type == "calculator":
            generated_code = f"""
def {request.tool_type}_tool():
    print("Calculator tool generated")
    return "Calculator functionality"
"""
        elif request.tool_type == "converter":
            generated_code = f"""
def {request.tool_type}_tool():
    print("Converter tool generated")
    return "Converter functionality"
"""
        else:
            generated_code = f"""
def {request.tool_type}_tool():
    print("Generic tool generated")
    return "Generic functionality"
"""
        
        return ToolResponse(
            tool_id=tool_id,
            tool_type=request.tool_type,
            generated_code=generated_code,
            status="generated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)