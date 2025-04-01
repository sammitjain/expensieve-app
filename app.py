# Setup and Import Libraries
from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import pandas as pd
from werkzeug.utils import secure_filename
from PIL import Image
import pdf2image
import openai
from dotenv import load_dotenv
import base64
import json

# Configure Flask App
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['PROCESSED_FOLDER'] = 'static/processed/'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)


# Load API key from .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
useOpenAI = True
if useOpenAI:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Cached JSON response for testing
CACHED_RESPONSE = {
    "Image Preview": "static/processed/coffee_airport_814.jpg",  # Path to a sample image
    "Extracted Data": {
        "Amount": "814",
        "City": "New Delhi",
        "Currency": "INR",
        "Date": "24/03/2025",
        "Expense Type": "Meal",
        "Payment Mode": "Card",
        "Remarks": "This is a cached response - For testing only",
        "Time of Transaction": "05:12 PM",
        "Vendor": "Tata Starbucks Private Limited"
    }
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(filepath):
    """ Resize image to a reasonable size. """
    image = Image.open(filepath)
    image.thumbnail((1024, 1024))  # Resize while maintaining aspect ratio
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], os.path.basename(filepath))
    image.save(processed_path)
    return processed_path

@app.route('/')
def index():
    return render_template('index.html')

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def process_receipt(file):
    """Processes a single receipt file and returns extracted data."""
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Convert PDF to image if needed
    if filename.lower().endswith('.pdf'):
        images = pdf2image.convert_from_path(filepath)
        if images:
            image_path = filepath.replace('.pdf', '.jpg')
            images[0].save(image_path, 'JPEG')
            filepath = image_path  # Use converted image for processing

    # Process and resize the image
    processed_image_path = process_image(filepath)

    # Encode the processed image as base64
    base64_image = encode_image(processed_image_path)

    if useOpenAI:
        # Make OpenAI API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        { "type": "text", "text": """
                            You are an AI assistant that extracts structured data from receipts.
                            Given an image of a receipt, always return a JSON object with the following fields in this order: 
                            Date, Expense Type, Vendor, City, Currency, and Amount. 
                            If available, also extract Payment Mode and Time of Transaction. 
                            In most cases receipts are from within India - so you can guess INR from the city.
                            The date should always be in DD/MM/YYYY format (Indian style). 
                            Restrict Expense Type to:
                            1. Cab/Ground Transportation
                            2. Meal
                            3. Hotel
                            4. Telecom (for phone bills, etc.)
                            5. Other (mention remarks)
                            If any field is missing or unclear, leave it as null and mention it in the 'Remarks' field. 
                            Do not guess missing values. Format the output as JSON. The response should contain only JSON.
                        """ },
                        {
                            "type": "image_url",
                            "image_url": { "url": f"data:image/jpeg;base64,{base64_image}" },
                        },
                    ],
                }
            ],
        )

        # Extract JSON from OpenAI response
        raw_extracted_data = response.choices[0].message.content.strip()

        # Ensure it's not empty before parsing
        if not raw_extracted_data:
            return {"error": "OpenAI returned an empty response"}

        # Remove triple backticks if present
        if raw_extracted_data.startswith("```json") and raw_extracted_data.endswith("```"):
            raw_extracted_data = raw_extracted_data[7:-3].strip()

        # Try to parse JSON
        try:
            extracted_data = json.loads(raw_extracted_data)
        except json.JSONDecodeError as e:
            return {"error": "Failed to parse OpenAI response", "details": str(e)}

        return {
            "Image Preview": f"/{processed_image_path}",
            "Extracted Data": extracted_data
        }
    
    return CACHED_RESPONSE  # Use cached response if OpenAI is disabled

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({"error": "No files uploaded"}), 400
    
    files = request.files.getlist('files')  # Get all uploaded files

    if not files or all(file.filename == '' for file in files):
        return jsonify({"error": "No selected files"}), 400

    results = []
    for file in files:
        if file and allowed_file(file.filename):
            receipt_data = process_receipt(file)
            results.append(receipt_data)
        else:
            results.append({"error": f"Invalid file format: {file.filename}"})

    return jsonify(results)  # Return a list of extracted receipts

@app.route('/static/processed/<filename>')
def serve_processed_image(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

CSV_FILE = "expenses.csv"
@app.route('/save', methods=['POST'])
def save_to_csv():
    data_list = request.json  # JSON received from frontend (should be a list of receipts)

    # Define CSV headers
    headers = ["Date", "Expense Type", "Vendor", "City", "Currency", "Amount", "Payment Mode", "Time of Transaction", "Remarks"]
    
    # Convert list of extracted receipt data into DataFrame
    df = pd.DataFrame([{key: receipt.get(key, "") for key in headers} for receipt in data_list])

    # Check if CSV exists and write accordingly
    file_exists = os.path.exists(CSV_FILE)
    df.to_csv(CSV_FILE, mode='a', index=False, header=not file_exists)

    return jsonify({"message": "Data saved successfully", "spreadsheet": df.to_dict(orient="records")})

if __name__ == '__main__':
    app.run(debug=True)
