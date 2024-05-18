import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from openai import OpenAI
import json
import os
import platform

# Configure the OpenAI API
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Path to Tesseract executable (if it's not in your PATH)
# Determine the path to the Tesseract executable based on the operating system
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
elif platform.system() == 'Darwin':  # macOS
    pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
else:  # Linux (including Heroku)
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

def convert_pdf_to_images(pdf_path):
    print("Converting PDF to images...")
    images = convert_from_path(pdf_path)
    print(f"Converted {len(images)} pages to images.")
    return images

def apply_ocr_to_images(images, start_page):
    pages_text = []
    for i, image in enumerate(images):
        page_num = start_page + i
        print(f"Applying OCR to page {page_num + 1}...")
        custom_config = r'--oem 3 --psm 3'
        text = pytesseract.image_to_string(image, config=custom_config)
        pages_text.append((page_num, text))
    return pages_text

def identify_summons_page_range(pages_text):
    combined_text = "\n".join([f"Page {page_num + 1}:\n{text}" for page_num, text in pages_text])
    prompt = (
        f"I'm going to give you text that contains legal documents, for which we only care about the summons"
        f"The idea is to identify the range of page numbers containing JUST the summons."
        f"You are to analyze what comes before and after to make sure you get all pages containing the summons text"
        f"The page containing the 'field sheet' should always be discarded from the final range as should the 'complaint'. given that the summons is usually anywhere in between,"
        f"It is imperative to provide just the range of pages that have the summons. always exclude the 'complaint' pages. Make sure to include all summons disclaimers and law firm signatures."
        f"If this is not a legal document or summons, then use the null format below."
        f"Here is the legal document text:\n\n{combined_text}\n\n"
        f"Please provide the range in the format '{{\"start_page\": X, \"end_page\": Y}}' or '{{\"start_page\": X}}' if it's a single page."
        f"If no summons pages are identified, please respond with '{{\"start_page\": null, \"end_page\": null}}'. "
    )
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    max_tokens=4096)
    summons_info = response.choices[0].message.content.strip()
    print(f"Summons Info: {summons_info}")  # Debugging print statement

    # Extract page numbers range from the JSON response
    try:
        # Extract JSON from the response
        start_idx = summons_info.find("{")
        end_idx = summons_info.rfind("}") + 1
        json_str = summons_info[start_idx:end_idx]
        summons_range = json.loads(json_str)

        start_page = summons_range['start_page'] - 1  # Convert to 0-based index
        end_page = summons_range['end_page'] - 1  # Convert to 0-based index and keep it inclusive
        return start_page, end_page
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error parsing summons range: {e}")
        return None, None

def create_pdf_with_summons(original_pdf_path, start_page, end_page, output_pdf_path):
    document = fitz.open(original_pdf_path)
    new_doc = fitz.open()

    if start_page is None or end_page is None:
        print("No summons pages identified.")
        return

    print(f"Creating PDF with pages from {start_page + 1} to {end_page + 1}")
    new_doc.insert_pdf(document, from_page=start_page, to_page=end_page)

    if new_doc.page_count > 0:
        new_doc.save(output_pdf_path)
        print(f"Summons extracted and saved to {output_pdf_path}")
    else:
        print("No pages were added to the new document.")

def process_document(input_pdf_path, output_pdf_path):
    images = convert_pdf_to_images(input_pdf_path)
    num_pages = len(images)
    pages_text = []

    for i in range(0, num_pages, 20):
        chunk_images = images[i:i + 20]
        chunk_text = apply_ocr_to_images(chunk_images, i)
        pages_text.extend(chunk_text)

        start_page, end_page = identify_summons_page_range(chunk_text)
        if start_page is not None and end_page is not None:
            create_pdf_with_summons(input_pdf_path, start_page, end_page, output_pdf_path)
            return  # Exit the loop and return the document immediately

    print(f"Summons not found in the document: {input_pdf_path}")

