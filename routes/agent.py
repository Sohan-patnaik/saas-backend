from fastapi import APIRouter, HTTPException
<<<<<<< HEAD
from controllers.agent_controller import AgentController
from pydantic import BaseModel
import traceback
=======
from fastapi.responses import StreamingResponse
from backend.controllers.agent_controller import AgentController
from pydantic import BaseModel
import traceback

>>>>>>> 91acf44 (added chat stream api)
router = APIRouter()


class ChatRequest(BaseModel):
    msg: str
    bot_id: str


@router.post("/chat")
def chat(request: ChatRequest):
<<<<<<< HEAD

    try:

        controller = AgentController(request.bot_id)

        result = controller.run(request.msg)

=======
    try:
        controller = AgentController(request.bot_id)
        result = controller.run(request.msg)
>>>>>>> 91acf44 (added chat stream api)
        return {
            "bot_id": request.bot_id,
            "reply": result.get("answer"),
            "contexts": result.get("contexts"),
            "latency": result.get("latency")
        }
<<<<<<< HEAD

=======
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/stream")
def stream_chat(request: ChatRequest):
    try:
        controller = AgentController(request.bot_id)
        return StreamingResponse(
            controller.stream_run(request.msg),
            media_type="text/plain"
        )
>>>>>>> 91acf44 (added chat stream api)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )