# import os
# import shutil
# from legal_processor import LegalDocumentProcessor, RAGApplication

# # Define local folders for file storage and vector database
# UPLOAD_FOLDER = "legal_documents"
# VECTOR_DB_FOLDER = "legal_db"

# # Clean up vector DB folder if it exists (for a new session) and create UPLOAD_FOLDER if not present
# if os.path.exists(VECTOR_DB_FOLDER):
#     shutil.rmtree(VECTOR_DB_FOLDER)
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# # Create a global instance of LegalDocumentProcessor
# processor = LegalDocumentProcessor()

# def qa_upload_file(file_obj):
#     """
#     Saves the uploaded file to UPLOAD_FOLDER and indexes it in the vector database.
#     Expects file_obj to be a file-like object with a 'filename' attribute.
#     Returns the saved file path and a status message.
#     """
#     if file_obj is None:
#         return None, "No file uploaded."
    
#     filename = file_obj.filename if hasattr(file_obj, "filename") else file_obj.name
#     save_path = os.path.join(UPLOAD_FOLDER, filename)
    
#     with open(save_path, "wb") as f:
#         shutil.copyfileobj(file_obj, f)
    
#     # Index the file in the vector database.
#     processor.store_in_chroma([save_path])
#     print("File uploaded and processed successfully.")
#     return save_path, f"File successfully uploaded and processed at {save_path}"

# def qa_answer_question(file_path, question):
#     """
#     Given the stored file path and a question, sets up the retriever and runs the QA chain.
#     Returns the final answer.
#     """
#     if not file_path or not os.path.exists(file_path):
#         return "File not found. Please upload a document first."
#     if not question:
#         return "Please input a valid question."
    
#     retriever = processor.setup_retrievers()
#     rag_app = RAGApplication(retriever)
#     doc_texts, final_answer = rag_app.run(question)
#     return final_answer

import os
import shutil
from legal_processor import LegalDocumentProcessor, RAGApplication

# Update the folder path to match your app.py UPLOAD_FOLDER.
UPLOAD_FOLDER = "tmp"
VECTOR_DB_FOLDER = "legal_db"

# Clean up vector DB folder if it exists (for a new session) and create UPLOAD_FOLDER if not present.
if os.path.exists(VECTOR_DB_FOLDER):
    shutil.rmtree(VECTOR_DB_FOLDER)
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Create a global instance of LegalDocumentProcessor using the new folder.
processor = LegalDocumentProcessor()

def qa_upload_file(file_obj):
    """
    Saves the uploaded file to UPLOAD_FOLDER and indexes it in the vector database.
    Expects file_obj to be a file-like object with a 'filename' attribute.
    Returns the saved file path and a status message.
    """
    if file_obj is None:
        return None, "No file uploaded."
    
    filename = file_obj.filename if hasattr(file_obj, "filename") else file_obj.name
    save_path = os.path.join(filename)
    
    print(save_path)
    # with open(save_path, "wb") as f:
    #     shutil.copyfileobj(file_obj, f)
    
    # Index the file in the vector database.
    processor.store_in_chroma([save_path])
    print("File uploaded and processed successfully.")
    return save_path

def qa_answer_question(question):
    """
    Given the stored file path and a question, sets up the retriever and runs the QA chain.
    Returns the final answer.
    """
    # if not file_path or not os.path.exists(file_path):
    #     return "File not found. Please upload a document first."
    # if not question:
    #     return "Please input a valid question."
    
    retriever = processor.setup_retrievers()
    rag_app = RAGApplication(retriever)
    doc_texts, final_answer = rag_app.run(question)
    return final_answer