import magic
import tempfile
from pdfminer.high_level import extract_text

def validate_file_type(file, allowed_mimes):
    file.file.seek(0)
    mime = magic.from_buffer(file.file.read(2048), mime=True)
    file.file.seek(0)
    if mime not in allowed_mimes:
        raise ValueError(f"Unsupported file type: {mime}")

def extract_pdf_text(file_path: str) -> str:
    return extract_text(file_path)