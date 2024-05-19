import sys
from summons_extractor import process_document

if len(sys.argv) != 4:
    print("Usage: python summons_cli.py <input_pdf_path> <output_pdf_path> <model>")
    print("Model can be 'gpt' or 'gemini'")
    sys.exit(1)

input_pdf_path = sys.argv[1]
output_pdf_path = sys.argv[2]
model = sys.argv[3]

if model not in ["gpt", "gemini"]:
    print("Invalid model specified. Model can be 'gpt' or 'gemini'.")
    sys.exit(1)

process_document(input_pdf_path, output_pdf_path, model)

