# Summons Extractor

A Python-based application for extracting summons pages from legal PDF documents. This project includes both a command-line interface (CLI) and a web server application for processing PDF files and extracting the relevant pages containing the summons.

## Features

- Extracts only the summons pages from legal documents.
- Provides both a command-line interface and a web server application.
- Displays progress and status updates during PDF processing.
- Automatically downloads the processed PDF in the web application.

## Requirements

- Python 3.8 or higher
- Tesseract OCR
- Poppler-utils

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/summons-extractor.git
    cd summons-extractor
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv myenv
    source myenv/bin/activate  # Linux/macOS
    myenv\Scripts\activate  # Windows
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Install Tesseract OCR:**

    - **Linux:**

        ```bash
        sudo apt-get install tesseract-ocr
        sudo apt-get install poppler-utils
        ```

    - **macOS:**

        ```bash
        brew install tesseract
        brew install poppler
        ```

    - **Windows:**

        - Download and install Tesseract from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).
        - Add the Tesseract installation path to your system's PATH environment variable.
        - Download and install Poppler for Windows from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/).
        - Add the Poppler installation path to your system's PATH environment variable.

5. **Set the OpenAI API Key:**

    ```bash
    export OPENAI_API_KEY='your-openai-api-key'  # Linux/macOS
    set OPENAI_API_KEY='your-openai-api-key'  # Windows
    ```

6. **Set the Google Gemini API Key:**

    ```bash
    export GEMINI_API_KEY='your-gemini-api-key'  # Linux/macOS
    set GEMINI_API_KEY='your-gemini-api-key'  # Windows
    ```


## Usage

### Command-Line Interface (CLI)

1. **Run the CLI:**

    ```bash
    python summons_cli.py <input_pdf_path> <output_pdf_path>
    ```

    **Example:**

    ```bash
    python summons_cli.py documents/sample.pdf results/sample-summons.pdf gpt4
    ```

### Web Server Application

1. **Run the web server:**

    ```bash
    python app.py
    ```

2. **Open your web browser and navigate to:**

    ```
    http://127.0.0.1:5001/
    ```

3. **Upload a PDF file and observe the progress. The processed PDF will be available for download once the processing is complete.**



