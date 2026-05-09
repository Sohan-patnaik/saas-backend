from fastapi import APIRouter, HTTPException
from backend.controllers.agent_controller import AgentController
from pydantic import BaseModel
import traceback
router = APIRouter()


class ChatRequest(BaseModel):
    msg: str
    bot_id: str


@router.post("/chat")
def chat(request: ChatRequest):

    try:

        controller = AgentController(request.bot_id)

        result = controller.run(request.msg)

        return {
            "bot_id": request.bot_id,
            "reply": result.get("answer"),
            "contexts": result.get("contexts"),
            "latency": result.get("latency")
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )