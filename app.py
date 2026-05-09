from backend.routes.upload import router as UploadRouter
from backend.routes.agent import router as AgentRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Master AI",
    version="1.0"
)

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UploadRouter, prefix="/create-bot", tags=["Bots"])

app.include_router(AgentRouter, prefix="/chat", tags=["Agent"])


@app.get("/api")
def main():
    return {"status": "AI MASTER RUNNING..."}