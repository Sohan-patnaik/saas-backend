from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from supabase import create_client
from dotenv import load_dotenv
import os
import re
import uuid
from backend.controllers.ingestion_controller import IngestionController

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/create-bot")
async def create_bot(
    bot_name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...)
):

    try:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        content = await file.read()

        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", bot_name)

        user_id = "default_user"

        unique_id = str(uuid.uuid4())[:8]

        storage_path = f"bot-files/{user_id}/{safe_name}_{unique_id}.pdf"

        try:
            supabase.storage.from_("bot-files").upload(
                storage_path,
                content,
                {
                    "content-type": "application/pdf",
                    "upsert": "true"
                }
            )
        except Exception as e:
            print("Supabase upload error:", e)
            raise HTTPException(status_code=500, detail=f"Storage upload failed: {e}")

        file_path = os.path.join(UPLOAD_DIR, f"{safe_name}_{unique_id}.pdf")

        with open(file_path, "wb") as f:
            f.write(content)

        bot_id = f"{safe_name}_{unique_id}"
        try:
            controller = IngestionController(file_path, bot_id)
            controller.build_vectorstore()
        except Exception as e:
            print("Ingestion error:", e)
            raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

        bot_data = {
            "owner": user_id,
            "name": bot_name,
            "description": description,
            "file_name": file.filename,
            "storage_path": storage_path,
             "bot_id": bot_id
        }

        try:
            new_bot = supabase.table("bots").insert(bot_data).execute()
        except Exception as e:
            print("DB insert error:", e)
            raise HTTPException(status_code=500, detail=f"DB insert failed: {e}")

        return {
            "message": "Bot created successfully",
            "bot": new_bot.data
        }

    except Exception as e:
        print("Unexpected error:", e)
        raise HTTPException(status_code=500, detail=str(e))