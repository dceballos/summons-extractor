import os
from flask import Flask, request, send_file, render_template, jsonify
import tempfile
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from summons_extractor import process_document, convert_pdf_to_images, apply_ocr_to_images, identify_summons_page_range_gpt, identify_summons_page_range_gemini, create_pdf_with_summons
import subprocess
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# Shared state to store processing status
processing_status = {}

executor = ThreadPoolExecutor(max_workers=4)

# Global variable to control the number of pages processed at a time
PAGES_PER_CHUNK = 20

def update_status(task_id, progress, status_message, file_ready=False, output_path=None, no_summons_found=False):
    status = {
        'progress': progress,
        'status_message': status_message,
        'file_ready': file_ready,
        'no_summons_found': no_summons_found
    }
    if output_path:
        status['output_path'] = output_path
    processing_status[task_id] = status
    print(f"Updated status for task {task_id}: {status}")  # Debugging print statement
    # Flush to ensure immediate output
    sys.stdout.flush()

def process_pdf(input_pdf_path, output_pdf_path, task_id, model):
    update_status(task_id, 0, "Converting PDF to images...")
    try:
        images = convert_pdf_to_images(input_pdf_path)
    except Exception as e:
        update_status(task_id, 0, f"Error converting PDF to images: {e}")
        return

    num_pages = len(images)
    pages_text = []

    for i in range(0, num_pages, PAGES_PER_CHUNK):
        chunk_images = images[i:i + PAGES_PER_CHUNK]
        update_status(task_id, int((i / num_pages) * 100), f"Applying OCR to pages {i+1}-{min(i+PAGES_PER_CHUNK, num_pages)}...")
        
        for j in range(0, len(chunk_images), 1):
            try:
                print(f"before apply ocr for {j}")
                chunk_text = apply_ocr_to_images([chunk_images[j]], i+j)
            except Exception as e:
                print(f"error #{e}")
                update_status(task_id, int((i / num_pages) * 100), f"Error applying OCR to pages {i+1}-{min(i+PAGES_PER_CHUNK, num_pages)}: {e}")
                return
            pages_text.extend(chunk_text)

            progress = int(((i+j)  / num_pages * 100))
            update_status(task_id, progress, f"Processing pages {i+1}-{min(i+PAGES_PER_CHUNK, num_pages)}...")

        start_page, end_page = None, None
        if model == "gpt":
            start_page, end_page = identify_summons_page_range_gpt(pages_text)
        elif model == "gemini":
            start_page, end_page = identify_summons_page_range_gemini(pages_text)
        else:
            update_status(task_id, progress, f"Unknown model: {model}")
            return

        if start_page is not None and end_page is not None:
            try:
                create_pdf_with_summons(input_pdf_path, start_page, end_page, output_pdf_path)
                update_status(task_id, 100, "Summons extracted and PDF created.", True, output_pdf_path)
            except Exception as e:
                update_status(task_id, 100, f"Error creating PDF with summons: {e}", True)
            return

    update_status(task_id, 100, "No summons found in the document.", True, no_summons_found=True)
    print(f"Summons not found in the document: {input_pdf_path}")

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        task_id = os.urandom(8).hex()
        model = request.form.get('model', 'gpt')  # Default to 'gpt' if model is not specified
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input_file:
            file.save(temp_input_file.name)
            input_pdf_path = temp_input_file.name
            output_pdf_path = input_pdf_path.replace('.pdf', '-summons.pdf')

            # Initialize the processing status
            update_status(task_id, 0, "Initializing...")

            executor.submit(process_pdf, input_pdf_path, output_pdf_path, task_id, model)

            return jsonify({'message': 'File uploaded and processing started.', 'task_id': task_id})

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    status = processing_status.get(task_id, {'progress': 0, 'status_message': 'Initializing...'})
    return jsonify(status)

@app.route('/download', methods=['GET'])
def download_file():
    path = request.args.get('path')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True, download_name='summons.pdf')
    return 'File not found', 404

@app.route('/check_tesseract', methods=['GET'])
def check_tesseract():
    try:
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True, check=True)
        return jsonify({'status': 'success', 'output': result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'status': 'error', 'output': e.output, 'error': str(e)})
    except FileNotFoundError as e:
        return jsonify({'status': 'error', 'error': 'Tesseract not found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5001)), debug=True)

