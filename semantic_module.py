import json
import uuid
import re
import torch
import numpy as np
from transformers import (AutoTokenizer,
                          AutoModelForSequenceClassification,
                          BatchEncoding,
                          TrainingArguments,
                          Trainer)
from datasets import Dataset
from data_preprocessing import rearrange_df  # Make sure this module is available

MAX_SEQUENCE_LENGTH = 512

def preprocess_function(batch, tokenizer: AutoTokenizer, context: bool) -> BatchEncoding:
    if context:
        inputs = tokenizer(batch['sentence'],
                           batch['context'],
                           padding="max_length",
                           truncation=True,
                           max_length=MAX_SEQUENCE_LENGTH)
    else:
        inputs = tokenizer(batch['sentence'],
                           padding="max_length",
                           truncation=True,
                           max_length=MAX_SEQUENCE_LENGTH)
    return inputs

def generate_json_from_doc(text):
    d = {"id": 1, "annotations": [{"result": []}], "data": {'text': text}}
    t = ""
    start = 0
    end = 0
    for i in range(len(text)):
        if text[i] != '.' or ((i - start) < 30):
            t += "'" if text[i] == "`" else text[i]
            continue
        end = i
        if len(t) > 0:
            l = {"id": str(uuid.uuid1()),
                 "value": {"start": start, "end": end, "text": t, "labels": [""]}}
            d["annotations"][0]["result"].append(l)
        t = ""
        start = i + 1
    return json.dumps(d)

def infer(filepath):
    # Read the document and generate a temporary JSON file
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    temp_json = generate_json_from_doc(text)
    temp_json_path = "./judgement.json"
    with open(temp_json_path, "w", encoding="utf-8") as jsonfile:
        jsonfile.write(temp_json)
    
    # Load the saved model and tokenizer
    model = AutoModelForSequenceClassification.from_pretrained("./saved_model/")
    tokenizer = AutoTokenizer.from_pretrained("./saved_tokenizer/")
    
    training_args = TrainingArguments(report_to="none", output_dir="./inf_output/")
    trainer = Trainer(model=model, tokenizer=tokenizer, args=training_args)
    
    # Load and preprocess the generated JSON data
    with open(temp_json_path, "r", encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)
    data_df = rearrange_df([data], max_len_context=MAX_SEQUENCE_LENGTH)
    dataset = Dataset.from_pandas(data_df.copy())
    dataset_data = dataset.map(
        preprocess_function,
        fn_kwargs={'tokenizer': tokenizer, 'context': True},
        batched=True,
        remove_columns=dataset.column_names
    )
    
    logits, _, _ = trainer.predict(dataset_data)
    # Map model output to label names
    id2label = {0: 'PREAMBLE', 1: 'NONE', 2: 'FAC', 3: 'ARG_RESPONDENT', 4: 'RLC',
                5: 'ARG_PETITIONER', 6: 'ANALYSIS', 7: 'PRE_RELIED', 8: 'RATIO',
                9: 'RPC', 10: 'ISSUE', 11: 'STA', 12: 'PRE_NOT_RELIED'}
    predictions = [np.argmax(pred) for pred in logits]
    
    # Assume data_df has a 'doc_id' and 'sentence' column
    data_df.reset_index(inplace=True)
    doc = data_df[data_df['doc_id'] == 1]
    outputs = []
    for s in range(len(doc)):
        idx = doc.index[s]
        label = id2label[predictions[idx]]
        # Use regex to extract words from the sentence
        sentence_words = re.findall(r'\S+', doc.iloc[idx]['sentence'])
        sentence_text = ' '.join(sentence_words)
        outputs.append((label, sentence_text))
    return outputs

def generate_html(text, label):
    label_colour_mapping = {
        'PREAMBLE': "silver", "NONE": "gray", "FAC": "lightsalmon",
        "ARG_RESPONDENT": "gold", "RLC": "lightyellow", "ARG_PETITIONER": "tan",
        "ANALYSIS": "wheat", "PRE_RELIED": "lime", "RATIO": "palegreen",
        "RPC": "beige", "ISSUE": "violet", "STA": "lightskyblue",
        "PRE_NOT_RELIED": "turquoise"
    }
    label_text_mapping = {
        'PREAMBLE': "Preamble", "NONE": "None", "FAC": "Facts",
        "ARG_RESPONDENT": "Arguments of the Respondent",
        "RLC": "Ruling of Lower Court", "ARG_PETITIONER": "Arguments of the Petitioner",
        "ANALYSIS": "Analysis", "PRE_RELIED": "Precedents Relied Upon",
        "RATIO": "Reasoning (Ratio) for the Decision", "RPC": "Ruling of the Present Court",
        "ISSUE": "Issue", "STA": "Statute", "PRE_NOT_RELIED": "Precedents Not Relied Upon"
    }
    # Replace newline characters with HTML line breaks
    text = text.replace("\n", "<br>")
    return f'<span title="{label_text_mapping[label]}" class="highlight" style="background-color:{label_colour_mapping[label]}">{text}.</span>'
