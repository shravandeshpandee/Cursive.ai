import os
import re
import google.auth
import language_tool_python
import spacy
from autocorrect import Speller
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Set credentials path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\minor project\your_project.json"

# Initialize NLP tools
tool = language_tool_python.LanguageTool("en-US")
nlp = spacy.load("en_core_web_sm")
spell = Speller(lang="en")

def authenticate_google():
    try:
        creds, _ = google.auth.default()
        return creds
    except Exception as e:
        return f"Authentication Error: {e}"

def upload_image_and_convert_to_doc(image_path, creds):
    try:
        drive_service = build("drive", "v3", credentials=creds)
        file_metadata = {
            "name": "OCR_Converted_Doc",
            "mimeType": "application/vnd.google-apps.document",
        }
        media = MediaFileUpload(image_path, mimetype="image/jpeg")
        file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        return file.get("id")
    except Exception as e:
        return f"Error uploading to Google Docs: {e}"

def extract_text_from_doc(doc_id, creds):
    try:
        docs_service = build("docs", "v1", credentials=creds)
        drive_service = build("drive", "v3", credentials=creds)

        document = docs_service.documents().get(documentId=doc_id).execute()
        text = ""

        for content in document.get("body", {}).get("content", []):
            if "paragraph" in content:
                for element in content["paragraph"]["elements"]:
                    if "textRun" in element:
                        text += element["textRun"]["content"]

        drive_service.files().delete(fileId=doc_id).execute()
        return text.strip()
    except Exception as e:
        return f"Error extracting text: {e}"

def clean_and_correct_text(extracted_text):
    """Clean OCR text, fix spelling errors only in lowercase words, and correct grammar."""

    # Step 1: Clean line breaks
    text = extracted_text.replace('\r', '')
    text = re.sub(r'\n{2,}', '<PARA>', text)
    text = re.sub(r'\n+', ' ', text)
    text = text.replace('<PARA>', '\n\n')
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 2: Light spelling correction (ONLY for non-proper nouns)
    corrected_words = []
    for word in text.split():
        # Skip correcting if word starts with uppercase (likely proper noun)
        if word.islower():
            corrected_words.append(spell(word))
        else:
            corrected_words.append(word)
    text = ' '.join(corrected_words)

    # Step 3: Grammar correction
    matches = tool.check(text)
    corrected_text = language_tool_python.utils.correct(text, matches)

    return corrected_text



