import re
import os
import torch
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader

class LegalDocumentProcessor:
    def __init__(self, storage_folder="tmp"):
        self.storage_folder = storage_folder
        self.vector_store_directory = "legal_db"
        # Use OllamaEmbeddings by default; alternatively, you can use HuggingFaceEmbeddings.
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    def extract_case_number_and_split(self, file_path):
        if file_path.lower().endswith((".pdf", ".docx", ".doc", ".txt", ".PDF")):
            if file_path.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.lower().endswith((".docx", ".doc")):
                loader = UnstructuredWordDocumentLoader(file_path)
            else:
                loader = TextLoader(file_path)
            
            documents = loader.load()
            full_content = " ".join([doc.page_content.replace('\n', ' ') for doc in documents])
            # Remove unwanted URLs and patterns
            patterns = [r'https?://\S+', r'Indian Kanoon - http://indiankanoon.org/doc/\d+']
            for pattern in patterns:
                full_content = re.sub(pattern, '', full_content)
            number_patterns = [
                r"\bNOS?\.\s*(\d+[-\d+]*)",
                r"\bNo\.\s*(\d+[-\d+]*)",
                r"Equivalent citations:\s*([\w\s\d,]+),"
            ]
            case_numbers = []
            for pattern in number_patterns:
                matches = re.finditer(pattern, full_content[0:2000], re.IGNORECASE)
                for match in matches:
                    case_numbers.extend([m for m in match.groups() if m])
            case_number = case_numbers[0] if case_numbers else "Unknown"
            split_point = full_content.find("J U D G M E N T")
            header, judgment = (full_content[:split_point], full_content[split_point + 12:]) if split_point != -1 else ("", full_content)
            return header.strip(), judgment.strip(), case_number
        else:
            raise ValueError("Unsupported file format. Only PDF, Word, and TXT files are supported.")

    def create_chunks(self, file_path, chunk_size=1000, chunk_overlap=200):
        header, judgment, case_number = self.extract_case_number_and_split(file_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        metadata = [{"source": case_number}]
        docs = []
        if header:
            docs.extend(splitter.create_documents(texts=[header], metadatas=metadata))
        docs.extend(splitter.create_documents(texts=[judgment], metadatas=metadata))
        if docs:
            bench_pattern = re.compile(r'Bench:', re.IGNORECASE | re.MULTILINE)
            if not bench_pattern.search(docs[0].page_content):
                docs[-1].page_content += "  (judges part of the bench in this case)  "
        return docs

    def add_new_files(self, file_paths):
        all_docs = []
        for file_path in file_paths:
            try:
                docs = self.create_chunks(file_path)
                all_docs.extend(docs)
            except ValueError as e:
                print(f"Error processing {file_path}: {e}")
        return all_docs

    def store_in_chroma(self, file_paths):
        chunks = self.add_new_files(file_paths)
        chroma_db = Chroma.from_documents(chunks, self.embeddings, persist_directory=self.vector_store_directory)
        chroma_db.persist()
        print(f"File(s) saved to {self.vector_store_directory}")

    def setup_retrievers(self):
        # Load the persisted vector store.
        chroma_db = Chroma(persist_directory=self.vector_store_directory, embedding_function=self.embeddings)
        # Process documents from the storage folder (fallback)
        print([os.path.join(self.storage_folder, f) for f in os.listdir(self.storage_folder)
                                        if os.path.isfile(os.path.join(self.storage_folder, f))])
        documents = self.add_new_files([os.path.join(self.storage_folder, f) for f in os.listdir(self.storage_folder)
                                        if os.path.isfile(os.path.join(self.storage_folder, f))])
        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 3
        chroma_retriever = chroma_db.as_retriever(search_kwargs={"k": 3})
        ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, chroma_retriever], weights=[0.5, 0.5])
        return ensemble_retriever

class RAGApplication:
    def __init__(self, retriever):
        self.retriever = retriever
        self.llm = ChatOllama(model="deepseek-r1:1.5b", temperature=0)
        self.prompt = PromptTemplate(
            template="""You are an assistant for Indian legal question answering.
Use the following context to answer the question. If you don't know the answer, just say that you don't know.
Question: {question}
Context: {context}
Answer:""",
            input_variables=["question", "context"]
        )
        self.rag_chain = self.prompt | self.llm | StrOutputParser()

    def run(self, question):
        context = self.retriever.invoke(question)
        doc_texts = [doc.page_content for doc in context]
        answer = self.rag_chain.invoke({"question": question, "context": doc_texts})
        final_answer = re.sub(r'<think>.*?</think>', '', answer, flags=re.DOTALL).strip()
        return doc_texts, final_answer

# def answer_question(file_path, question):
#     """
#     Given a legal document file_path and a question:
#       1. Index the document into the vector database.
#       2. Set up the retriever.
#       3. Run the RAG chain to generate an answer.
#     Returns the final answer.
#     """
#     processor = LegalDocumentProcessor()
#     processor.store_in_chroma([file_path])
#     retriever = processor.setup_retrievers()
#     rag_app = RAGApplication(retriever)
#     doc_texts, final_answer = rag_app.run(question)
#     return final_answer