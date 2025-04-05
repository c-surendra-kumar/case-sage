import re
import torch
from transformers import LEDTokenizer, LEDForConditionalGeneration
import spacy
from spacy import displacy

def load_ner_model():
    # Adjust the model path as needed.
    ner_model_path = "model-best-3"
    return spacy.load(ner_model_path)

def load_summarization_model():
    # Adjust the model identifier/path as needed.
    tokenizer = LEDTokenizer.from_pretrained("legal_abs_model")
    model = LEDForConditionalGeneration.from_pretrained("legal_abs_model")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    if torch.cuda.is_available():
        model = model.half()
    # Ensure a padding token is defined.
    tokenizer.pad_token = tokenizer.eos_token
    return tokenizer, model

def clean_summary(summary):
    # Ensure summary ends with a full stop.
    if not summary.endswith('.'):
        summary = re.sub(r"\s[^.]*$", "", summary)
    return summary

def extractive_summary(text, ner_model):
    doc = ner_model(text)
    from collections import defaultdict
    sentence_scores = defaultdict(float)
    for sent in doc.sents:
        for ent in sent.ents:
            sentence_scores[sent] += 1
    num_sentences = 50  # adjust as needed
    top_sentences = sorted(sentence_scores.keys(), key=lambda x: sentence_scores[x], reverse=True)[:num_sentences]
    summary = " ".join(str(sent) for sent in top_sentences)
    return clean_summary(summary)

def abstractive_summary(text, tokenizer, model):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=9000).to(device)
    summary_ids = model.generate(
        **inputs,
        max_length=1024,
        min_length=100,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    summary_final = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return clean_summary(summary_final)

def abstractive_summary_hybrid(text, tokenizer, model):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=2048).to(device)
    summary_ids = model.generate(
        **inputs,
        max_length=1024,
        min_length=100,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    summary_final = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return clean_summary(summary_final)

def combined_summary(text, ner_model, tokenizer, model):
    extractive_sum = extractive_summary(text, ner_model)
    return abstractive_summary_hybrid(extractive_sum, tokenizer, model)

def get_summary(text, method="Abstractive"):
    """
    Returns a summary of the given text based on the chosen method.
    """
    if method == "Extractive":
        ner_model = load_ner_model()
        if "sentencizer" not in ner_model.pipe_names:
            ner_model.add_pipe("sentencizer")
        return extractive_summary(text, ner_model)
    elif method == "Abstractive":
        tokenizer, model = load_summarization_model()
        return abstractive_summary(text, tokenizer, model)
    elif method == "Extractive-Abstractive":
        ner_model = load_ner_model()
        if "sentencizer" not in ner_model.pipe_names:
            ner_model.add_pipe("sentencizer")
        tokenizer, model = load_summarization_model()
        return combined_summary(text, ner_model, tokenizer, model)
    else:
        return "Invalid summarization method specified"

def visualize_ner(text):
    """
    Uses spaCy's displacy to generate an HTML visualization of named entities.
    """
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    html = displacy.render(doc, style="ent", page=True)
    return html
