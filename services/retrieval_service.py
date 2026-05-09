from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

import pickle
import os


class Retrieval:

    def __init__(self, bot_id: str):

        self.bot_id = bot_id

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        self.vector_store = None
        self.docs = None
        self.retriever = None

        self.base_path = f"backend/vectorstore/{bot_id}"
        self.chunks_path = f"{self.base_path}/chunks.pkl"
        self.faiss_path = f"{self.base_path}/faiss_index"

    def chunk(self, docs):

        chunks = self.splitter.split_documents(docs)
        self.docs = chunks

        return chunks

    def _build_retriever(self):

        if self.vector_store is None or self.docs is None:
            raise ValueError("Vector store or docs not initialized")

        vector_retriever = self.vector_store.as_retriever(
            search_kwargs={"k": 6}
        )

        bm25_retriever = BM25Retriever.from_documents(self.docs)
        bm25_retriever.k = 6

        self.retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.5, 0.5]
        )

    def store(self, chunks, embedding):

        self.docs = chunks

        os.makedirs(self.base_path, exist_ok=True)

        with open(self.chunks_path, "wb") as f:
            pickle.dump(chunks, f)

        self.vector_store = FAISS.from_documents(
            chunks,
            embedding
        )

        self.vector_store.save_local(self.faiss_path)

        self._build_retriever()

    def load(self, embedding):

        if not os.path.exists(self.faiss_path):
            raise ValueError("Vector store not found. Run ingestion first.")

        self.vector_store = FAISS.load_local(
            self.faiss_path,
            embedding,
            allow_dangerous_deserialization=True
        )

        if os.path.exists(self.chunks_path):
            with open(self.chunks_path, "rb") as f:
                self.docs = pickle.load(f)

        if self.docs is None:
            raise ValueError("Chunks missing. Run store() first.")

        self._build_retriever()

    def retrieve(self, query):

        if self.retriever is None:
            raise ValueError("Retriever not initialized.")

        docs = self.retriever.invoke(query)

        return docs[:3]