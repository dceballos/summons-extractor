import fitz  # PyMuPDF
import requests
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

def model_prompt(combined_text):
    return f"""
    I'm going to provide you with the text content of pages from a legal document.
    Please identify the pages that contain the 'Summons', including disclaimers and law firm signatures.
    Return a JSON payload in the form of {{"start": x, "end": x}} where 'start' and 'end' correspond with the
    page ranges (inclusively). If it's only 1 page, they should be the same. If there
    is no summons or the document is not even a legal document, return null for
    'start' and 'end'. 

    Page Content:

    {combined_text}
    """

def identify_summons_page_range(pages_text):
    combined_text = "\n".join([f"Page {page_num + 1}:\n{text}" for page_num, text in pages_text])
    prompt = model_prompt(combined_text)

    response = client.chat.completions.create(model="gpt-4-turbo",
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

        start_page = summons_range['start'] - 1  # Convert to 0-based index
        end_page = summons_range['end'] - 1  # Convert to 0-based index and keep it inclusive
        return start_page, end_page
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Error parsing summons range: {e}")
        return None, None

def identify_summons_page_range_gemini(pages_text):
    """Identifies summons pages in a PDF using the Gemini API."""
    combined_text = "\n".join([f"Page {page_num + 1}:\n{text}" for page_num, text in pages_text])
    api_url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=AIzaSyCS8rmBkmsrsPMenPn-jkY6c8O3T58mr5o"
    prompt = model_prompt(combined_text)

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "contents": [{ "parts": [{"text": prompt}]}]
    }

    response = requests.post(api_url, headers=headers, json=data)

    print(response.text)
    if response.status_code == 200:
        result = response.json()
        r = json.loads(result["candidates"][0]["content"]["parts"][0]["text"])
        return r["start"] - 1, r["end"] - 1
    else:
        raise Exception(f"Gemini API request failed with status code: {response.status_code}")


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

