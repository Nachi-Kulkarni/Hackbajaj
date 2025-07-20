import os
import base64
from dotenv import load_dotenv
from mistralai import Mistral

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("MISTRAL_API_KEY")

if not api_key:
    raise ValueError("No MISTRAL_API_KEY found in .env file")

# Setup
client = Mistral(api_key=api_key)

# Path to your local file
file_path = "dataset/dataset1.pdf"

# Read the file and encode it in base64
with open(file_path, "rb") as file:
    document_base64 = base64.b64encode(file.read()).decode("utf-8")

# Process document using the correct format for base64 PDFs
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{document_base64}"
    },
    include_image_base64=True
)

print(ocr_response)
