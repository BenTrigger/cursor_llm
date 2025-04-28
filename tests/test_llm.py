import unittest
import os
import yaml
import sys
import traceback
import torch
from openai import OpenAI, RateLimitError
from llama_cpp import Llama

class TestLLMBackends(unittest.TestCase):
    def setUp(self):
        try:
            # Load configuration
            with open('config.yaml', 'r') as f:
                self.config = yaml.safe_load(f)
            
            print("Configuration loaded successfully")
            
            # Initialize OpenAI client
            self.openai_client = OpenAI(api_key=self.config['llm']['openai']['api_key'])
            print("OpenAI client initialized")
            
            # Initialize Llama if configured
            self.llama_model = None
            if self.config['llm']['backend'] == 'llama':
                try:
                    model_path = self.config['llm']['llama']['model_path']
                    print(f"Attempting to load Llama model from: {model_path}")
                    
                    # Check if file exists
                    if not os.path.exists(model_path):
                        raise FileNotFoundError(f"Model file not found at: {model_path}")
                    
                    # Check file extension
                    if not model_path.lower().endswith('.gguf'):
                        print("\nERROR: Model file must be in GGUF format (.gguf extension)")
                        print("You have two options:")
                        print("1. Download a pre-converted GGUF model from:")
                        print("   https://huggingface.co/TheBloke")
                        print("2. Convert your existing model using llama.cpp tools")
                        print("   (This requires additional setup)")
                        raise ValueError("Model must be in GGUF format")
                    
                    self.llama_model = Llama(
                        model_path=model_path,
                        n_ctx=self.config['llm']['llama']['context_size'],
                        n_gpu_layers=0 if self.config['llm']['llama']['device'] == 'cpu' else -1
                    )
                    print("Llama model initialized successfully")
                except Exception as e:
                    print(f"Warning: Could not initialize Llama model: {str(e)}")
                    print("Traceback:")
                    traceback.print_exc()
        except Exception as e:
            print(f"Error in setUp: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

    def test_gpu_availability(self):
        """Test if GPU is available and can be used"""
        try:
            print("\nTesting GPU availability...")
            
            # Check if CUDA is available
            cuda_available = torch.cuda.is_available()
            print(f"CUDA available: {cuda_available}")
            
            if cuda_available:
                # Get GPU information
                gpu_count = torch.cuda.device_count()
                print(f"Number of GPUs: {gpu_count}")
                
                for i in range(gpu_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)  # Convert to GB
                    print(f"GPU {i}: {gpu_name}")
                    print(f"GPU {i} Memory: {gpu_memory:.2f} GB")
                
                # Test a simple CUDA operation
                x = torch.rand(5, 3).cuda()
                y = torch.rand(5, 3).cuda()
                z = x + y
                print("Simple CUDA operation successful")
                
                if self.config['llm']['llama']['device'] == 'gpu':
                    print("\nGPU configuration is correct")
                    print("Note: For Llama.cpp, GPU support is enabled by default when CUDA is available")
                else:
                    print("\nWarning: GPU is available but not configured in config.yaml")
                    print("Consider setting device to 'gpu' in config.yaml")
            else:
                print("\nWarning: CUDA is not available")
                if self.config['llm']['llama']['device'] == 'gpu':
                    print("Error: GPU is configured but not available")
                    print("Please set device to 'cpu' in config.yaml")
                    raise ValueError("GPU configured but not available")
                else:
                    print("CPU mode is correctly configured")
            
            print("GPU test completed")
        except Exception as e:
            print(f"Error in test_gpu_availability: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

    def test_openai_connection(self):
        """Test OpenAI API connection"""
        try:
            print("Testing OpenAI connection...")
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            self.assertIsNotNone(response)
            self.assertIsNotNone(response.choices[0].message.content)
            print("OpenAI connection test passed!")
        except RateLimitError as e:
            print("\nERROR: OpenAI API quota exceeded")
            print("Please check your OpenAI account:")
            print("1. Visit https://platform.openai.com/account/billing")
            print("2. Add payment method if needed")
            print("3. Or get a new API key with available credits")
            raise
        except Exception as e:
            print(f"Error in test_openai_connection: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

    def test_llama_connection(self):
        """Test Llama model connection"""
        if self.llama_model is None:
            print("Skipping Llama test - model not configured")
            return
            
        try:
            print("Testing Llama model...")
            response = self.llama_model("Hello", max_tokens=5)
            self.assertIsNotNone(response)
            self.assertIn('choices', response)
            print("Llama connection test passed!")
        except Exception as e:
            print(f"Error in test_llama_connection: {str(e)}")
            print("Traceback:")
            traceback.print_exc()
            raise

if __name__ == '__main__':
    unittest.main() 