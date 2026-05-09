from langchain_community.document_loaders import PyPDFLoader


class Ingestion:

    def __init__(self, files):
        self.files = files

    def scrape(self):

        documents = []

        for file in self.files:
            loader = PyPDFLoader(file)
            docs = loader.load()
            documents.extend(docs)

        return documents