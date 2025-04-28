import pdfplumber
import logging

logger = logging.getLogger(__name__)

def extract_text(file_path):
    try:
        logger.info(f"Extracting text from PDF: {file_path}")
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        logger.info(f"Successfully extracted text from PDF: {file_path}")
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
        raise 