from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

_global_rag_chain = None

class RAG:
    def __init__(self):
        global _global_rag_chain
        if _global_rag_chain is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")

            model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0,
                google_api_key=api_key
            )

            prompt = ChatPromptTemplate.from_messages([
                ("system",
                 """You are a reliable FAQ assistant. Answer questions ONLY using the provided context.

Rules:
- Use only the context
- Do not use outside knowledge
- If answer is not found say: "I don't know based on the provided document."
- Do not hallucinate
- Provide clear structured answers
"""),
                ("human",
                 """Context:
{context}

Chat History:
{history}

Question:
{query}
""")
            ])

            parser = StrOutputParser()
            _global_rag_chain = prompt | model | parser

        self.chain = _global_rag_chain

    def _format_context(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def run(self, docs, query, history):
        if not docs:
            return "I don't know based on the provided document."

        context = self._format_context(docs)
        return self.chain.invoke({
            "context": context,
            "query": query,
            "history": history,
        })

    def stream_run(self, docs, query, history):
        if not docs:
            yield "I don't know based on the provided document."
            return

        context = self._format_context(docs)
        for chunk in self.chain.stream({
            "context": context,
            "query": query,
            "history": history,
        }):
            yield chunk
