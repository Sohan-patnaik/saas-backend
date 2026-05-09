from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()


class RAG:

    def __init__(self):

        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")

        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             """
You are a reliable FAQ assistant. Answer questions ONLY using the provided context.

Rules:
- Use only the context
- Do not use outside knowledge
- If answer is not found say: "I don't know based on the provided document."
- Do not hallucinate
- Provide clear structured answers
"""),

            ("human",
             """
Context:
{context}

Chat History:
{history}

Question:
{query}
""")
        ])

        self.parser = StrOutputParser()

        self.chain = self.prompt | self.model | self.parser

    def _format_context(self, docs):

        return "\n\n".join(
            doc.page_content for doc in docs
        )

    def run(self, docs, query,history):

        if not docs:
            return "I don't know."

        context = self._format_context(docs)

        result = self.chain.invoke({
            "context": context,
            "query": query,
            "history": history,
        })

        return result
