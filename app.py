from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Ensure backend directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.upload import router as UploadRouter
from routes.agent import router as AgentRouter
from routes.billing import router as BillingRouter

app = FastAPI(
    title="HowYouThink AI Master API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UploadRouter, prefix="/create-bot", tags=["Bots"])
app.include_router(AgentRouter, prefix="/chat", tags=["Agent"])
app.include_router(BillingRouter, prefix="/billing", tags=["Billing"])

@app.get("/api")
def health_check():
    return {"status": "AI MASTER RUNNING..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)