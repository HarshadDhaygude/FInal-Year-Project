from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import mysql.connector
import logging

app = Flask(__name__)

# Setup paths and allowed file types
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set the correct path for Tesseract (ensure it's installed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Helper function to validate uploaded files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Serve the index page
@app.route('/')
def home():
    try:
        return render_template('home.html')  # Ensure home.html exists in the templates folder
    except Exception as e:
        logging.error(f"Error serving index page: {e}")
        return "Error: Unable to load the index page.", 500
@app.route('/index')
def index():
    return render_template('index.html')

# Handle image upload and processing


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            extracted_text = pytesseract.image_to_string(Image.open(filepath)).strip()
            cleaned_text = extracted_text.replace("\n", " ").lower()

            if not cleaned_text:
                return jsonify({"error": "No text found in the image"}), 400

            # conn = mysql.connector.connect(
            #     host="localhost",
            #     user="root",
            #     password="Yadav@123",
            #     database="ingredient_db"
            # )
            conn = mysql.connector.connect(
                host="shortline.proxy.rlwy.net",
                port=59867,
                user="root",
                password="SaGzejNBHlXVTYLghHCWuaErbkwwCvba",
                database="ingredient_db"
              )
            cursor = conn.cursor()

            ingredients = [item.strip() for item in cleaned_text.split(",")]
            query = """
                SELECT `Ingredient Name`, `Chemical Name`, `Is Harmful`, `Description`, 
                       `Affected Body Parts`, `Percentage Effect`, `Food Sources` 
                FROM ingredientdatabase 
                WHERE `Ingredient Name` LIKE %s
            """

            results = []
            for ingredient in ingredients:
                cursor.execute(query, (f"%{ingredient}%",))
                results.extend(cursor.fetchall())

            cursor.close()
            conn.close()

            # Pass extracted text and results to result.html
            return render_template("result.html", extracted_text=extracted_text, results=results)

        except Exception as e:
            logging.error(f"Error during processing: {e}")
            return jsonify({"error": f"An error occurred while processing your request: {e}"}), 500

    return jsonify({"error": "Invalid file format"}), 400



# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)

