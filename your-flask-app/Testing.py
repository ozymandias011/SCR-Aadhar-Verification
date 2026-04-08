import os
from ultralytics import YOLO
from huggingface_hub import hf_hub_download
import cv2
import numpy as np
from PIL import Image
import pytesseract
import logging
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Repo details and model loading
repo_config = {
    "repo_id": "arnabdhar/YOLOv8-nano-aadhar-card",
    "filename": "model.pt",
    "local_dir": "./models"
}
model = YOLO(hf_hub_download(**repo_config))
id2label = model.names

def verhoeff_algorithm(aadhaar_number):
    d = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    p = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
    c = 0
    aadhaar_number = aadhaar_number[::-1]
    for i in range(len(aadhaar_number)):
        c = d[c][p[i % 8][int(aadhaar_number[i])]]
    return c == 0

def process_aadhar_card(file_path):
    try:
        logging.info(f"Processing Aadhar card: {file_path}")
        image = Image.open(file_path)
        image_np = np.array(image)
        results = model.predict(image_np)
        
        aadhar_number = None
        extracted_data = {}
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls)
                label = id2label[class_id]
                bbox = box.xyxy.tolist()[0]
                x_min, y_min, x_max, y_max = map(int, bbox)
                roi = image_np[y_min:y_max, x_min:x_max]
                text = pytesseract.image_to_string(roi).strip()
                
                if label == "AADHAR_NUMBER":
                    aadhar_number = ''.join(filter(str.isdigit, text))
                    extracted_data['aadhar_number'] = aadhar_number
                    print(f"Aadhar number: {aadhar_number}")
                else:
                    extracted_data[label.lower()] = text
        
        if aadhar_number:
            is_valid = verhoeff_algorithm(aadhar_number)
            extracted_data['is_valid'] = is_valid
            logging.info(f"Verification result: {'Valid' if is_valid else 'Invalid'}")
            return 'Valid' if is_valid else 'Invalid', aadhar_number
            
        logging.warning("No Aadhar number detected")
        return None, None
        
    except Exception as e:
        logging.error(f"Error processing Aadhar card: {e}")
        return False, None

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify_aadhar():
    try:
        if 'aadhar_document' not in request.files:
            logging.info('No file part in the request')
            return redirect(url_for('home'))
        
        file = request.files['aadhar_document']
        
        if file.filename == '':
            logging.info('No selected file')
            return redirect(url_for('home'))
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logging.info(f"File saved to {file_path}")
            
            verification_result, aadhar_number = process_aadhar_card(file_path)
            logging.info(f'Verification result: {verification_result}, Aadhar number: {aadhar_number}')
            
            if verification_result == 'Valid':
                logging.info('Aadhar verification successful.')
                return render_template('success.html', aadhar_number=aadhar_number)
            else:
                logging.info('Aadhar verification failed.')
                return render_template('failure.html', aadhar_number=aadhar_number)
        else:
            logging.warning('Unsupported file type uploaded.')
            return render_template('error.html', message='Unsupported file type.')
    except Exception as e:
        logging.error(f'Error during verification: {e}')
        return render_template('error.html', message='An unexpected error occurred.')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server = request.environ.get('werkzeug.server.shutdown')
    if shutdown_server is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logging.info(f"Created upload directory at {UPLOAD_FOLDER}")
    app.run(debug=True)