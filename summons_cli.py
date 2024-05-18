import sys
from summons_extractor import process_document

if len(sys.argv) != 3:
    print("Usage: python summons_cli.py <input_pdf_path> <output_pdf_path>")
    sys.exit(1)

input_pdf_path = sys.argv[1]
output_pdf_path = sys.argv[2]

process_document(input_pdf_path, output_pdf_path)
