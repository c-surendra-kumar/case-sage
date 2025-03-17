import os
from semantic_module import infer, generate_html

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_text(filepath, action, question):
    """
    Process the uploaded file according to the specified action.
    Currently supports:
      - 'summarization': Uses abstractive summarization.
      - 'semantic': Runs semantic segmentation.
      - 'qa': Placeholder for question answering.
      - 'similarity': Placeholder for similarity analysis.
    """
    if action == 'summarization':
        return "QA functionality not implemented yet"
        # # For summarization, read the text and generate a summary.
        # with open(filepath, 'r', encoding='utf-8') as f:
        #     text = f.read()
        # tokenizer, model = load_summarization_model()
        # return abstractive_summary(text, tokenizer, model)
    elif action == 'semantic':
        # For semantic segmentation, call the infer function.
        outputs = infer(filepath)
        # For each (label, sentence) pair, generate an HTML snippet.
        html_results = "".join(generate_html(sentence, label) + "<br>" for label, sentence in outputs)
        return html_results
    elif action == 'qa':
        # Add your QA function call here.
        return "QA functionality not implemented yet"
    elif action == 'similarity':
        # Add your similarity function call here.
        return "Similarity functionality not implemented yet"
    else:
        return "No valid action specified"