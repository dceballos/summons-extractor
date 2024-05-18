import os
from flask import Flask, request, send_file, render_template, jsonify
import tempfile
import threading
from time import sleep
from summons_extractor import convert_pdf_to_images, apply_ocr_to_images, identify_summons_page_range, create_pdf_with_summons

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

# Shared state to store processing status
processing_status = {}

def process_pdf(input_pdf_path, output_pdf_path, task_id):
    images = convert_pdf_to_images(input_pdf_path)
    num_pages = len(images)
    pages_text = []

    for i in range(0, num_pages, 20):
        chunk_images = images[i:i + 20]
        chunk_text = apply_ocr_to_images(chunk_images, i)
        pages_text.extend(chunk_text)

        progress = int((i + 20) / num_pages * 100)
        processing_status[task_id] = {'progress': progress}

        start_page, end_page = identify_summons_page_range(chunk_text)
        if start_page is not None and end_page is not None:
            create_pdf_with_summons(input_pdf_path, start_page, end_page, output_pdf_path)
            processing_status[task_id] = {'progress': 100, 'file_ready': True, 'output_path': output_pdf_path}
            return

    processing_status[task_id] = {'progress': 100, 'file_ready': True, 'output_path': output_pdf_path}
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
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_input_file:
            file.save(temp_input_file.name)
            input_pdf_path = temp_input_file.name
            output_pdf_path = input_pdf_path.replace('.pdf', '-summons.pdf')

            # Initialize the processing status
            processing_status[task_id] = {'progress': 0}

            thread = threading.Thread(target=process_pdf, args=(input_pdf_path, output_pdf_path, task_id))
            thread.start()

            return jsonify({'message': 'File uploaded and processing started.', 'task_id': task_id})

@app.route('/status/<task_id>', methods=['GET'])
def check_status(task_id):
    status = processing_status.get(task_id, {'progress': 0})
    return jsonify(status)

@app.route('/download', methods=['GET'])
def download_file():
    path = request.args.get('path')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True, download_name='summons.pdf')
    return 'File not found', 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

