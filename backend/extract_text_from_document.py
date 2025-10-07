import os
import fitz  # PyMuPDF
import pdfplumber
import docx

def extract_text_from_pdf(file_path):
    # Try PyMuPDF first
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
        if text.strip():
            return text
    except Exception as e:
        print(f"[WARN] PyMuPDF failed: {e}")
    # Fallback to pdfplumber
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        if text.strip():
            return text
    except Exception as e:
        print(f"[WARN] pdfplumber failed: {e}")
    return text

def extract_text_from_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"[WARN] python-docx failed: {e}")
    return text

def extract_text(file_path, output_path=None):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    if not text.strip():
        print("[WARN] No text extracted.")
    out_path = output_path or file_path + "_extracted.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Extracted text saved to {out_path}")
    return text

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python extract_text_from_document.py <file_path> [output_path]")
        exit(1)
    file_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    extract_text(file_path, output_path)
