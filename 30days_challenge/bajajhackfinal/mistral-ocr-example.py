import os
from mistralai import Mistral

# Setup
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

# Process document
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": "path/to/your/insurance/document.pdf"
    },
    include_image_base64=True
)
