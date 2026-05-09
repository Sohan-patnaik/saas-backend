from backend.services.embedding_service import EmbeddingService
from backend.services.retrieval_service import Retrieval
from backend.controllers.rag_controller import RAG
import time
from supabase import create_client
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
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

        context = "\n\n".join(contexts) if contexts else "No relevant context found."

        history_res = supabase.table("conversations") \
        .select("user_message,bot_reply") \
        .eq("bot_id", self.bot_id) \
        .order("created_at") \
        .limit(10) \
        .execute()

        history = "\n".join(
            f"User: {row['user_message']}\nBot: {row['bot_reply']}"
            for row in history_res.data
        )

        result = self.rag.run(context_docs, query,history)
        self.history.append(f"User: {query}")
        self.history.append(f"Bot: {result}")

        latency = time.time() - start
        supabase.table("conversations").insert({
        "bot_id": self.bot_id,
        "user_message": query,
        "bot_reply": result
    }).execute()

        return {
            "question": query,
            "answer": result,
            "contexts": contexts,
            "latency": latency
        }