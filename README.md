# LLM File QA

A Flask web application that allows you to upload files (.txt, .pdf, .docx, .xlsx) and ask questions about their content using an LLM (OpenAI or Llama).

## Features

- Upload and process various file types (.txt, .pdf, .docx, .xlsx)
- Ask questions about file content
- Choose between OpenAI API and Llama (CPU/GPU) for LLM
- Comprehensive logging system
- REST API endpoints for integration
- Modern web interface

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/llm-file-qa.git
   cd llm-file-qa
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the application:
   - Copy `config.yaml.example` to `config.yaml`
   - Edit `config.yaml` to set your OpenAI API key or Llama model path
   - Choose the LLM backend (OpenAI or Llama) and device (CPU/GPU)

5. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Configuration

The `config.yaml` file allows you to:
- Switch between OpenAI and Llama backends
- Set the OpenAI API key
- Configure Llama for CPU or GPU usage
- Adjust Flask server settings

Example configuration:
```yaml
llm:
  backend: "openai"  # Options: "openai" or "llama"
  openai:
    api_key: "your-openai-api-key-here"
  llama:
    device: "gpu"  # Options: "cpu" or "gpu"
    model_path: "path/to/your/llama/model"
    context_size: 2048
```

## Logging

The application includes comprehensive logging:
- Logs are stored in the `logs/` directory
- Rotating file handler with 10 backup files
- Log levels: INFO, WARNING, ERROR
- Detailed error tracking and debugging information

## API Endpoints

- `GET /`: Web interface
- `POST /upload`: Upload files
- `GET /files`: List uploaded files
- `POST /ask`: Ask questions about file content

## File Extraction

The application uses the following libraries for file extraction:
- `pdfplumber` for PDF files
- `python-docx` for Word documents
- `openpyxl` for Excel files
- Built-in for text files

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 