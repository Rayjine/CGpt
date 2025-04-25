from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file (assume same as ensembl_mcp_server)
load_dotenv(
    dotenv_path=os.path.join(os.path.dirname(__file__), "ensembl_mcp_server", ".env")
)

from client.ensembl_client import EnsemblClient

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ensemble_client = EnsemblClient()


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    result: Any
    error: Optional[str] = None


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest = Body(...)):
    try:
        answer = ensemble_client.query(request.query)
        return ChatResponse(result=answer)
    except Exception as e:
        return ChatResponse(result=None, error=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010)
