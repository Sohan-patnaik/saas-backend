from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()


class EmbeddingService:

    def __init__(self):
        self.embedding = NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-e5-v5",
            api_key=os.getenv("NVIDIA_API_KEY"),
            truncate="END",
        )

    def get_embedding(self):
        return self.embedding
