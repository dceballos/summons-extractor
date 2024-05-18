import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from openai import OpenAI

client = OpenAI(api_key='sk-proj-IegKzcdzZNQlnuJjesPVT3BlbkFJ7EH8lN7JH017GEQLFeDw')
import json
import os

# Configure the OpenAI API

# Path to Tesseract executable (if it's not in your PATH)
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

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
        text = pytesseract.image_to_string(image)
        pages_text.append((page_num, text))
    return pages_text

def identify_summons_page_range(pages_text):
    combined_text = "\n".join([f"Page {page_num + 1}:\n{text}" for page_num, text in pages_text])
    prompt = (
        f"I'm going to give you legal documents that contain a field sheet and a jury summons. "
        f"The idea is to identify the range of page numbers containing JUST the summons. We are to extract just the pages that contain the summons. make sure to include all "
        f" pages that belong to the summons.  you are to analyze what comes before and after to make sure you get all summons pages"
        f"The page containing the 'field sheet' should always be discarded from the final range as should the complaint. given that the summons is usually anywhere in between,"
        f"It is imperative to still provide a range of pages that have only the summons. always exclude the complaint pages. We just want summon pages inclusively, including all disclaimers and lawfirm signatures."
        f"Here is the legal document text:\n\n{combined_text}\n\n"
        f"Please provide the range in the format '{{\"start_page\": X, \"end_page\": Y}}' or '{{\"start_page\": X}}' if it's a single page."
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

def process_documents(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            input_pdf_path = os.path.join(input_folder, filename)
            output_pdf_path = os.path.join(output_folder, filename)
            main(input_pdf_path, output_pdf_path)

def main(input_pdf_path, output_pdf_path):
    images = convert_pdf_to_images(input_pdf_path)
    num_pages = len(images)
    pages_text = []

    for i in range(0, num_pages, 20):
        chunk_images = images[i:i + 20]
        chunk_text = apply_ocr_to_images(chunk_images, i)
        pages_text.extend(chunk_text)

        # Identify the summons range in this chunk
        start_page, end_page = identify_summons_page_range(chunk_text)
        print(f"Identified summons page range: start_page={start_page}, end_page={end_page}")  # Debugging print statement
        if start_page is not None and end_page is not None:
            create_pdf_with_summons(input_pdf_path, start_page, end_page, output_pdf_path)
            return  # Exit the loop and return the document immediately

    print(f"Summons not found in the document: {input_pdf_path}")

# Example usage
input_folder = "documents"
output_folder = "results"
process_documents(input_folder, output_folder)
