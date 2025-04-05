import os
import glob
import torch
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer, util
from transformers import BartForConditionalGeneration, BartTokenizer

def compute_similarity(filepath):
    output_html = ""
    
    # ---- Extract text from PDF using PyPDF ----
    try:
        reader = PdfReader(filepath)
    except Exception as e:
        return f"<p>Error reading PDF: {e}</p>"
    
    query_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            query_text += text + " "
    
    if not query_text.strip():
        return "<p>Error: No text could be extracted from the uploaded document.</p>"
    
    # Display a preview of the extracted text.
    preview = query_text[:500] + ("..." if len(query_text) > 500 else "")
    output_html += f"<h3>Extracted Text (Preview)</h3><p>{preview}</p>"
    
    # ---- Load the Fine-Tuned Similarity Model ----
    output_html += "<p>Loading similarity model...</p>"
    similarity_model = SentenceTransformer("fine_tuned_similarity_model_ver2.0")
    query_embedding = similarity_model.encode(query_text, convert_to_tensor=True)
    
    # ---- Load Dataset Documents ----
    output_html += "<p>Loading dataset documents...</p>"
    dataset_path = "data"
    doc_files = sorted(glob.glob(os.path.join(dataset_path, "*.txt")))
    if not doc_files:
        return "<p>Error: No documents found in the dataset folder.</p>"
    
    doc_texts = []
    doc_names = []
    for file in doc_files:
        # try:
        with open(file, "r") as f:
            text = f.read()
            doc_texts.append(text)
            doc_names.append(os.path.basename(file))
        # except Exception as e:
        #     output_html += f"<p>Warning: Could not read {file}: {e}</p>"
    
    if not doc_texts:
        return "<p>Error: No readable documents were loaded from the dataset.</p>"
    
    # ---- Load Precomputed Embeddings ----
    output_html += "<p>Loading precomputed document embeddings...</p>"
    try:
        loaded_obj = torch.load("document_embeddings_text+entity.pt")
    except Exception as e:
        return f"<p>Error loading embeddings: {e}</p>"
    
    if isinstance(loaded_obj, dict):
        if "embeddings" in loaded_obj:
            doc_embeddings = loaded_obj["embeddings"]
        else:
            return f"<p>Error: Embeddings file is a dict but does not contain key 'embeddings'. Found keys: {', '.join(loaded_obj.keys())}</p>"
    else:
        doc_embeddings = loaded_obj

    # ---- Compute Similarity Scores ----
    cosine_scores = util.cos_sim(query_embedding, doc_embeddings)[0]
    top_results = torch.topk(cosine_scores, k=5)

    output_html += '<h2 class="subheader">Top 5 Similar Documents</h2>'
    
    # # ---- Load BART Model for Summarization ----
    # output_html += "<p>Loading summarization model...</p>"
    # bart_model_name = "facebook/bart-large-cnn"
    # bart_tokenizer = BartTokenizer.from_pretrained(bart_model_name)
    # bart_model = BartForConditionalGeneration.from_pretrained(bart_model_name)
    
    # ---- Loop over the top similar documents and build HTML output ----
    for score, idx in zip(top_results[0], top_results[1]):
        doc_name = doc_names[idx]
        sim_score = score.item()
        doc_text = doc_texts[idx]
        
        # # Summarize the document using BART
        # input_ids = bart_tokenizer.encode(doc_text, truncation=True, max_length=1024, return_tensors="pt")
        # summary_ids = bart_model.generate(input_ids, max_length=60, min_length=20, do_sample=False)
        # summary = bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        
        card_html = f"""
        <div class="document-card">
          <h4 class="subheader">{doc_name}</h3>
          <br>
          <h4 class="similarity-score">Similarity Score: {sim_score:.4f}</h4>
          <br>
          <p> {doc_text[:300]}</p>
          <br>
          <br>
        </div>
        """
        output_html += card_html
    
    return output_html
