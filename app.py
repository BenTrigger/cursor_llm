from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import yaml
from openai import OpenAI
from llama_cpp import Llama
import json
import logging
from logging.handlers import RotatingFileHandler
from collections import deque
import threading
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a deque to store recent logs (last 1000 messages)
log_buffer = deque(maxlen=1000)

# Custom handler to store logs in memory
class MemoryHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))

    def emit(self, record):
        log_buffer.append(self.format(record))

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Add file handler
file_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10240,
    backupCount=10,
    mode='a',
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Add memory handler
memory_handler = MemoryHandler()
memory_handler.setLevel(logging.INFO)
logger.addHandler(memory_handler)

# Load configuration
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    logger.info("Configuration loaded successfully")
except Exception as e:
    logger.error(f"Error loading configuration: {str(e)}")
    raise

# Initialize Flask app
app = Flask(__name__)
logger.info("Flask app initialized")

# Initialize OpenAI client
client = OpenAI(api_key=config['llm']['openai']['api_key'])
logger.info("OpenAI client initialized")

# Initialize Llama if configured
llama_model = None
if config['llm']['backend'] == 'llama':
    try:
        llama_model = Llama(
            model_path=config['llm']['llama']['model_path'],
            n_ctx=config['llm']['llama']['context_size'],
            n_gpu_layers=0 if config['llm']['llama']['device'] == 'cpu' else -1
        )
        logger.info(f"Llama model initialized with device: {config['llm']['llama']['device']}")
    except Exception as e:
        logger.error(f"Error initializing Llama model: {str(e)}")
        raise

# Ensure data directory exists
os.makedirs('data', exist_ok=True)
logger.info("Data directory created/verified")

# Add session management
session_data = {
    'conversation_history': [],
    'current_file': None
}

@app.route('/')
def index():
    logger.info("Home page accessed")
    return render_template('index.html')

@app.route('/logs')
def get_logs():
    """Endpoint to fetch recent logs"""
    return jsonify({'logs': list(log_buffer)})

@app.route('/upload', methods=['POST'])
def upload_file():
    logger.info("File upload request received")
    if 'file' not in request.files:
        logger.warning("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.warning("No file selected")
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        try:
            file_path = os.path.join('data', file.filename)
            file.save(file_path)
            logger.info(f"File saved successfully: {file.filename}")
            return jsonify({'message': 'File uploaded successfully'}), 200
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({'error': 'Error saving file'}), 500

@app.route('/files', methods=['GET'])
def list_files():
    logger.info("File list request received")
    try:
        files = os.listdir('data')
        logger.info(f"Found {len(files)} files")
        return jsonify({'files': files})
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return jsonify({'error': 'Error listing files'}), 500

def get_file_extractor(file_path):
    """Get the appropriate extractor based on file extension."""
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.txt':
        from utils.extract_txt import extract_text
    elif file_ext == '.pdf':
        from utils.extract_pdf import extract_text
    elif file_ext == '.docx':
        from utils.extract_docx import extract_text
    elif file_ext == '.xlsx':
        from utils.extract_excel import extract_text
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    return extract_text

@app.route('/clear_session', methods=['POST'])
def clear_session():
    """Clear the current session data"""
    global session_data
    session_data = {
        'conversation_history': [],
        'current_file': None
    }
    # Clear the data directory
    try:
        shutil.rmtree('data')
        os.makedirs('data')
        logger.info("Session cleared successfully")
        return jsonify({'message': 'Session cleared successfully'})
    except Exception as e:
        logger.error(f"Error clearing session: {str(e)}")
        return jsonify({'error': 'Error clearing session'}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    logger.info("Question request received")
    data = request.json
    question = data.get('question')
    if not question:
        logger.warning("No question provided")
        return jsonify({'error': 'No question provided'}), 400

    try:
        files = os.listdir('data')
        if not files:
            logger.warning("No files available for question answering")
            return jsonify({'error': 'No files available'}), 400

        # Use the current file if available, otherwise get the first file
        current_file = session_data['current_file'] or files[0]
        file_path = os.path.join('data', current_file)
        logger.info(f"Processing question for file: {current_file}")
        
        try:
            extract_text = get_file_extractor(file_path)
            content = extract_text(file_path)
            logger.info(f"Content extracted from {current_file}")
        except Exception as e:
            logger.error(f"Error extracting content from {current_file}: {str(e)}")
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500

        # Add conversation history to the context
        conversation_context = "\n".join([f"Q: {q}\nA: {a}" for q, a in session_data['conversation_history']])
        full_context = f"{conversation_context}\n\nCurrent Context: {content}"

        if config['llm']['backend'] == 'openai':
            logger.info("Using OpenAI for question answering")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Previous conversation:\n{conversation_context}\n\nQuestion: {question}\nContext: {content}"}
                ]
            )
            answer = response.choices[0].message.content
        else:
            logger.info("Using Llama for question answering")
            prompt = f"Previous conversation:\n{conversation_context}\n\nQuestion: {question}\nContext: {content}"
            response = llama_model(prompt, max_tokens=100)
            answer = response['choices'][0]['text']

        # Update conversation history
        session_data['conversation_history'].append((question, answer))
        session_data['current_file'] = current_file

        logger.info("Question answered successfully")
        return jsonify({'answer': answer})
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        return jsonify({'error': 'Error processing question'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(
        host=config['flask']['host'],
        port=config['flask']['port'],
        debug=config['flask']['debug']
    ) 