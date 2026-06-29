from services.embedding_service import EmbeddingService
from services.retrieval_service import Retrieval
from controllers.rag_controller import RAG
import time
import threading
from supabase import create_client
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def _async_log_conversation(bot_id, query, reply):
    try:
        supabase.table("conversations").insert({
            "bot_id": bot_id,
            "user_message": query,
            "bot_reply": reply
        }).execute()
    except Exception as e:
        print("Async DB log error:", e)

class AgentController:
    def __init__(self, bot_id):
        self.bot_id = bot_id
        self.embedding = EmbeddingService()
        self.retrieval = Retrieval(bot_id)
        self.rag = RAG()
        self.history = []

        embedding = self.embedding.get_embedding()
        self.retrieval.load(embedding)

    def run(self, query):
        start = time.time()
        context_docs = self.retrieval.retrieve(query)
        contexts = [doc.page_content for doc in context_docs] if context_docs else []

        try:
            history_res = supabase.table("conversations") \
                .select("user_message,bot_reply") \
                .eq("bot_id", self.bot_id) \
                .order("created_at") \
                .limit(5) \
                .execute()
            history = "\n".join(
                f"User: {row['user_message']}\nBot: {row['bot_reply']}"
                for row in (history_res.data or [])
            )
        except Exception:
            history = ""

        result = self.rag.run(context_docs, query, history)
        latency = time.time() - start

        threading.Thread(target=_async_log_conversation, args=(self.bot_id, query, result)).start()

        return {
            "question": query,
            "answer": result,
            "contexts": contexts,
            "latency": latency
        }

    def stream_run(self, query):
        context_docs = self.retrieval.retrieve(query)

        try:
            history_res = supabase.table("conversations") \
                .select("user_message,bot_reply") \
                .eq("bot_id", self.bot_id) \
                .order("created_at") \
                .limit(5) \
                .execute()
            history = "\n".join(
                f"User: {row['user_message']}\nBot: {row['bot_reply']}"
                for row in (history_res.data or [])
            )
        except Exception:
            history = ""

        full_reply = []
        for chunk in self.rag.stream_run(context_docs, query, history):
            full_reply.append(chunk)
            yield chunk

        complete_bot_reply = "".join(full_reply)
        threading.Thread(target=_async_log_conversation, args=(self.bot_id, query, complete_bot_reply)).start()
