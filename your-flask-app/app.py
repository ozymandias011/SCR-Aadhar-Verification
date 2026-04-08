from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from Testing import process_aadhar_card
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('page2.html')

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

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logging.info(f"Created upload directory at {UPLOAD_FOLDER}")
    app.run(debug=True)