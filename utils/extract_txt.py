import logging

logger = logging.getLogger(__name__)

def extract_text(file_path):
    try:
        logger.info(f"Extracting text from {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        logger.info(f"Successfully extracted text from {file_path}")
        return content
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {str(e)}")
        raise 