import requests
import runpod  # Required
import base64
from typing import List

from server_commands import initialize_model, process_pdf_endpoint, process_image_endpoint, OCRResponse

        
initialize_model()

def handler(event):
    try:
        # Validate the input against the schema
        inputs: list = event["input"]["inputs"]
        results: List[OCRResponse] = []
        for item in inputs:
            file_type = item["file_type"]
            file_data = item.get("file_data", None)
            file_url = item.get("file_url", None)
            prompt = item.get("prompt", None)
            filename = "unknown"

            if not (file_type in ["pdf", "image"]):
                results.append(OCRResponse(success=False, error=f"Invalid file type: {file_type}, should be one of: pdf, image"))
                continue

            if file_url is not None:
                try:
                    data_bytes = requests.get(file_url).content
                    filename = file_url.split("/")[-1]
                except Exception as e:
                    results.append(OCRResponse(success=False, error=f"Error downloading file from URL: {file_url}: {str(e)}"))
                    continue
            elif file_data is not None:
                try:
                    data_bytes = base64.b64decode(file_data)
                except Exception as e:
                    results.append(OCRResponse(success=False, error=f"Error decoding file data: {str(e)}"))
                    continue
            else:
                results.append(OCRResponse(success=False, error="No file data or URL provided"))
                continue
            if file_type == "pdf":
                results.append(process_pdf_endpoint(data_bytes, prompt, filename))
            elif file_type == "image":
                results.append(process_image_endpoint(data_bytes, prompt))
            else:
                results.append(OCRResponse(success=False, error="Invalid request type, should be one of: pdf, image"))
        return {"output": [result.to_dict() for result in results]}
    except Exception as e:
        return {"error": str(e)}
    

runpod.serverless.start({"handler": handler})  # Required