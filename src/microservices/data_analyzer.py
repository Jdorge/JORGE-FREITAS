from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import openai
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Data Analyzer Microservice")

# Configurar OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatMessage(BaseModel):
    message: str
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

@app.get("/")
async def root():
    return {"message": "Data Analyzer Microservice is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    try:
        if not openai.api_key or openai.api_key == "sua-chave-openai":
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil que analisa dados e responde perguntas."},
                {"role": "user", "content": chat_message.message}
            ],
            max_tokens=1000
        )
        
        return ChatResponse(response=response.choices[0].message.content)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "data_analyzer"}