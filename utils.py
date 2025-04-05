import os
from summarization_module import get_summary  
from qa_module import qa_upload_file, qa_answer_question
from flask import request

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_text(filepath, action, question):
    # Read file text if needed (for summarization/semantic). For QA, we pass the file path.
    if action == 'summarization':
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        # Get the selected summarization method from the dropdown.
        method = request.form.get("method", "Abstractive")
        # Check whether to visualize entities.
        visualize = request.form.get("visualize_entities", "off") == "on"
        # Assume get_summary() and visualize_ner() are implemented in your summarization_module.
        from summarization_module import get_summary, visualize_ner
        summary = get_summary(text, method=method)
        if visualize:
            entities_html = visualize_ner(text)
            return summary + "<hr>" + entities_html
        else:
            return summary
    elif action == 'semantic':
        from semantic_module import infer, generate_html
        outputs = infer(filepath)
        html_results = "".join(generate_html(sentence, label) + "<br>" for label, sentence in outputs)
        return html_results
    elif action == "qa_upload":
        # For QA, upload and index the file.
        # Here we assume the file is already saved in 'filepath'
        with open(filepath, "rb") as f:
            return qa_upload_file(f)[1]
    elif action == "qa_query":
        # For QA, answer a question based on the already uploaded file.
        return qa_answer_question(question)
    elif action == 'similarity':
        from similarity_module import compute_similarity
        return compute_similarity(filepath)
    else:
        return "No valid action specified"
