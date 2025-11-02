import fitz  # PyMuPDF
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_road_issues(text):
    """Extracts potential road safety issues using simple NLP logic."""
    keywords = [
        "pothole", "crack", "overspeeding", "school", "curve", "sign", "lighting",
        "slippery", "intersection", "visibility", "barrier", "guardrail", "crosswalk",
        "shoulder", "narrow", "accident", "speed breaker", "reflector", "ramp", "pedestrian"
    ]
    found_issues = [word for word in keywords if word in text.lower()]
    return found_issues
