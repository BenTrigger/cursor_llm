import unittest
import os
import sys
import traceback
from utils.extract_txt import extract_text as extract_txt
from utils.extract_pdf import extract_text as extract_pdf
from utils.extract_docx import extract_text as extract_docx
from utils.extract_excel import extract_text as extract_excel

class TestFileExtractors(unittest.TestCase):
    def setUp(self):
        try:
            # Create test files
            self.test_dir = 'test_data'
            os.makedirs(self.test_dir, exist_ok=True)
            
            # Create test.txt
            with open(os.path.join(self.test_dir, 'test.txt'), 'w', encoding='utf-8') as f:
                f.write('This is a test text file.')
                
            print("Test setup completed successfully")
        except Exception as e:
            print(f"Error in setUp: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

    def test_txt_extractor(self):
        """Test the text file extractor"""
        try:
            file_path = os.path.join(self.test_dir, 'test.txt')
            print(f"Testing TXT extractor with file: {file_path}")
            
            content = extract_txt(file_path)
            print(f"Extracted content: {content[:100]}...")  # Print first 100 chars
            
            self.assertIsInstance(content, str)
            self.assertIn('test text file', content)
            print("TXT extractor test passed!")
        except Exception as e:
            print(f"Error in test_txt_extractor: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

    def test_pdf_extractor(self):
        """Test the PDF file extractor"""
        try:
            # This is a placeholder - you'll need to add a test PDF file
            print("PDF extractor test skipped - no test file available")
        except Exception as e:
            print(f"Error in test_pdf_extractor: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

    def test_docx_extractor(self):
        """Test the DOCX file extractor"""
        try:
            # This is a placeholder - you'll need to add a test DOCX file
            print("DOCX extractor test skipped - no test file available")
        except Exception as e:
            print(f"Error in test_docx_extractor: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

    def test_excel_extractor(self):
        """Test the Excel file extractor"""
        try:
            # This is a placeholder - you'll need to add a test Excel file
            print("Excel extractor test skipped - no test file available")
        except Exception as e:
            print(f"Error in test_excel_extractor: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

    def tearDown(self):
        try:
            # Clean up test files
            if os.path.exists(self.test_dir):
                for file in os.listdir(self.test_dir):
                    os.remove(os.path.join(self.test_dir, file))
                os.rmdir(self.test_dir)
            print("Test cleanup completed successfully")
        except Exception as e:
            print(f"Error in tearDown: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

if __name__ == '__main__':
    unittest.main() 