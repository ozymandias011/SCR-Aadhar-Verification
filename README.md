# Aadhar Verification Web App

A Flask-based web application for verifying Aadhar cards using computer vision and OCR.

## Project Structure

- `your-flask-app/app.py` - Main Flask application entry point.
- `your-flask-app/Testing.py` - Aadhar extraction and verification logic using YOLO, Tesseract OCR, and Verhoeff checksum validation.
- `your-flask-app/templates/` - HTML templates for upload, success, failure, and error pages.
- `your-flask-app/uploads/` - Folder where uploaded Aadhar images are stored.
- `your-flask-app/models/model.pt` - Pretrained YOLO model used for Aadhar field detection.

## Features

- Upload Aadhar image files (`.jpg`, `.jpeg`) from the web interface.
- Detect Aadhar number region using a YOLO model.
- Extract text using Tesseract OCR.
- Validate extracted Aadhar number with the Verhoeff algorithm.
- Display success or failure pages based on verification.

## Prerequisites

- Python 3.10+ recommended
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installed on Windows
- `pip` package manager

## Setup Instructions

1. Clone or copy the repository to your local machine.
2. Open a terminal in `SCR_Aadhar_verification`.
3. Create a virtual environment and activate it:

```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
```

4. Install required packages:

```powershell
pip install flask ultralytics huggingface-hub pytesseract opencv-python pillow numpy
```

5. Install Tesseract OCR on Windows, then verify the installation path.

6. If Tesseract is installed in a different location, update the path in `your-flask-app/Testing.py`:

```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Running the App

1. From `SCR_Aadhar_verification/your-flask-app`, run:

```powershell
python app.py
```

2. Open your browser and go to:

```text
http://127.0.0.1:5000/
```

3. Upload an Aadhar image and submit for verification.

## Notes

- Supported upload file types in `app.py` are `.jpg` and `.jpeg`.
- `Testing.py` supports `.pdf`, `.png`, `.jpg`, and `.jpeg` in its own `allowed_file` helper, but the main app currently only accepts `.jpg` and `.jpeg`.
- The project uses a pretrained YOLO model from Hugging Face: `arnabdhar/YOLOv8-nano-aadhar-card`.

## Troubleshooting

- If uploads fail, ensure `your-flask-app/uploads/` exists and the Flask app has permission to write to it.
- If OCR does not extract the Aadhar number, confirm Tesseract is installed and the image quality is good.
- For model download issues, ensure internet access is available or place the model at `your-flask-app/models/model.pt` if already downloaded.

## License

This repository is provided as-is for demonstration and prototype use.
