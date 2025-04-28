import unittest
import os
from app import app
import json

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        # Set up test client
        self.app = app.test_client()
        self.app.testing = True
        
        # Create test directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)

    def test_home_route(self):
        """Test the home route"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        print("Home route test passed!")

    def test_upload_route(self):
        """Test the file upload route"""
        # Create a test file
        test_file_path = 'test.txt'
        with open(test_file_path, 'w') as f:
            f.write('Test content')
        
        # Test file upload
        with open(test_file_path, 'rb') as f:
            response = self.app.post(
                '/upload',
                data={'file': (f, test_file_path)},
                content_type='multipart/form-data'
            )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        print("Upload route test passed!")
        
        # Clean up
        os.remove(test_file_path)
        if os.path.exists(os.path.join('data', test_file_path)):
            os.remove(os.path.join('data', test_file_path))

    def test_ask_route(self):
        """Test the question asking route"""
        # First upload a test file
        test_file_path = 'test.txt'
        with open(test_file_path, 'w') as f:
            f.write('This is a test file.')
        
        with open(test_file_path, 'rb') as f:
            self.app.post(
                '/upload',
                data={'file': (f, test_file_path)},
                content_type='multipart/form-data'
            )
        
        # Test asking a question
        response = self.app.post(
            '/ask',
            json={'question': 'What is this file about?'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('answer', data)
        print("Ask route test passed!")
        
        # Clean up
        os.remove(test_file_path)
        if os.path.exists(os.path.join('data', test_file_path)):
            os.remove(os.path.join('data', test_file_path))

    def tearDown(self):
        # Clean up test directories
        if os.path.exists('data'):
            for file in os.listdir('data'):
                os.remove(os.path.join('data', file))
            os.rmdir('data')
        if os.path.exists('logs'):
            for file in os.listdir('logs'):
                os.remove(os.path.join('logs', file))
            os.rmdir('logs')

if __name__ == '__main__':
    unittest.main() 