# import os
# import logging
# from flask import Flask, render_template, request, jsonify
# from werkzeug.utils import secure_filename
# from utils import process_text, allowed_file

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# app = Flask(__name__)
# app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max file size

# # Save uploaded files directly into the "legal_documents" folder.
# app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "legal_documents")
# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])

# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/semantic')
# def semantic():
#     return render_template('semantic.html')

# @app.route('/similarity')
# def similarity():
#     return render_template('similarity.html')

# @app.route('/summarization')
# def summarization():
#     return render_template('summarization.html')

# @app.route('/qa')
# def qa():
#     return render_template('qa.html')

# @app.route('/process', methods=['POST'])
# def process():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400

#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400

#         if not allowed_file(file.filename):
#             return jsonify({'error': 'Invalid file type'}), 400

#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)

#         action = request.form.get('action', '')
#         question = request.form.get('question', '')

#         # Delegate processing based on the action (e.g., "semantic", "qa_upload", "qa_query", etc.)
#         result = process_text(filepath, action, question)
#         # If you want to persist the file for later queries, do not delete it:
#         # os.remove(filepath)  # Uncomment if you want to clean up the file after processing.

#         return jsonify({'result': result})
#     except Exception as e:
#         logging.error(f"Error processing request: {str(e)}")
#         return jsonify({'error': 'An error occurred during processing'}), 500

# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('base.html', error="Page not found"), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('base.html', error="Internal server error"), 500

import os
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils import process_text, allowed_file
import shutil

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Use "tmp" as the upload folder (make sure it exists)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), "tmp")
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
        action = request.form.get('action', '')
        question = request.form.get('question', '')
        
        # For actions that require a file upload (qa_upload, summarization, semantic, similarity)
        if action in ["qa_upload", "summarization", "semantic", "similarity"]:
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
            result = process_text(filepath, action, question)
            # For actions other than qa_upload (if you want to persist the file for queries), you can remove the file.
            if action != 'qa_upload':
                os.remove(filepath)
            # if action in ["summarization", "semantic", "similarity"]:
            #     shutil.rmtree('tmp')
        # For query action, using our combined workflow, no file is uploaded.
        elif action == "qa_query":
            # In our new design, we don't need a file identifier – we use the last uploaded file.
            result = process_text("", action, question)
        else:
            result = "No valid action specified"
        
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

if __name__ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)



# import os
# import logging
# from flask import Flask, render_template, request, jsonify
# from werkzeug.utils import secure_filename
# from utils import process_text, allowed_file

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)

# app = Flask(__name__)
# app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
# app.config['UPLOAD_FOLDER'] = 'tmp'

# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/semantic')
# def semantic():
#     return render_template('semantic.html')

# @app.route('/similarity')
# def similarity():
#     return render_template('similarity.html')

# @app.route('/summarization')
# def summarization():
#     return render_template('summarization.html')

# @app.route('/qa')
# def qa():
#     return render_template('qa.html')

# @app.route('/process', methods=['POST'])
# def process():
#     try:
#         if 'file' not in request.files:
#             return jsonify({'error': 'No file uploaded'}), 400
        
#         file = request.files['file']
#         if file.filename == '':
#             return jsonify({'error': 'No file selected'}), 400
            
#         if not allowed_file(file.filename):
#             return jsonify({'error': 'Invalid file type'}), 400

#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(filepath)

#         action = request.form.get('action', '')
#         question = request.form.get('question', '')

#         result = process_text(filepath, action, question)
#         os.remove(filepath)  # Clean up uploaded file

#         return jsonify({'result': result})

#     except Exception as e:
#         logging.error(f"Error processing request: {str(e)}")
#         return jsonify({'error': 'An error occurred during processing'}), 500

# @app.errorhandler(404)
# def not_found_error(error):
#     return render_template('base.html', error="Page not found"), 404

# @app.errorhandler(500)
# def internal_error(error):
#     return render_template('base.html', error="Internal server error"), 500
