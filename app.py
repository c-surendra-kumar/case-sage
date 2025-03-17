import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils import process_text, allowed_file

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'tmp'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/semantic')
def semantic():
    return render_template('semantic.html')

@app.route('/similarity')
def similarity():
    return render_template('similarity.html')

@app.route('/summarization')
def summarization():
    return render_template('summarization.html')

@app.route('/qa')
def qa():
    return render_template('qa.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        action = request.form.get('action', '')
        question = request.form.get('question', '')

        result = process_text(filepath, action, question)
        os.remove(filepath)  # Clean up uploaded file

        return jsonify({'result': result})

    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({'error': 'An error occurred during processing'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('base.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', error="Internal server error"), 500
