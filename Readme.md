Yes, let's include all the files and directories you mentioned in the project structure section of the README file. Here's the updated README.md:

### README.md

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

## Usage

### Command-Line Interface (CLI)

1. **Run the CLI:**

    ```bash
    python summons_cli.py <input_pdf_path> <output_pdf_path>
    ```

    **Example:**

    ```bash
    python summons_cli.py documents/sample.pdf results/sample-summons.pdf
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

## Project Structure

```
summons-extractor/
│
├── Readme.md                # Project README file
├── app.py                   # Main web server application
├── myenv/                   # Virtual environment directory
├── summons_cli.py           # Command-line interface script
├── summons_extractor.py     # PDF processing and OCR functions
├── __pycache__/             # Python cache files
├── documents/               # Folder containing input PDF documents
├── results/                 # Folder for storing output PDF documents
├── templates/               # HTML templates for the web application
│   └── upload.html          # HTML template for the web application
└── static/
    └── style.css            # CSS for the web application
```

## Summons Extractor Functions

- **convert_pdf_to_images**: Converts a PDF document to images for OCR processing.
- **apply_ocr_to_images**: Applies OCR to a list of images and extracts text.
- **identify_summons_page_range**: Identifies the page range containing the summons.
- **create_pdf_with_summons**: Creates a new PDF with only the summons pages.

## Example Commands

### Extract Summons Using CLI

```bash
python summons_cli.py documents/sample.pdf results/sample-summons.pdf
```

### Running the Web Server

```bash
python app.py
```

Open your browser and navigate to `http://127.0.0.1:5001/` to upload and process a PDF file.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License.

---

Feel free to update the repository URL and any other details specific to your project. This README provides clear instructions for installing, using, and contributing to the project.
