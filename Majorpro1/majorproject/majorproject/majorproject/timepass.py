
# from PIL import Image
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# image_path = "zinc.png"
# extracted_text = pytesseract.image_to_string(Image.open(image_path)).strip()
# print(f"Extracted text: {extracted_text}")



from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import mysql.connector

app = Flask(__name__)

# Setup paths and allowed file types
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Set the correct path for Tesseract (ensure it's installed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Check if the file is valid
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Serve the index page from the root folder
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')  # Correct way to serve from root directory

# Handle the file upload

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return "Error: No file part", 400
    
    file = request.files['image']
    if file.filename == '':
        return "Error: No selected file", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Use Tesseract to extract text from the image
            extracted_text = pytesseract.image_to_string(Image.open(filepath)).strip()

            # Check if OCR resulted in any text
            if not extracted_text:
                return "Error: No text found in the image", 400

            # Connect to the database
            conn = mysql.connector.connect(
                host="localhost",
                user="root",  # MySQL username
                password="Yadav@123",  # MySQL password
                database="mydatabase"  # Your MySQL database
            )
            cursor = conn.cursor()

            query = "SELECT * FROM project_table WHERE `Ingredient Name` LIKE %s"
            cursor.execute(query, (f"%{extracted_text}%",))
            results = cursor.fetchall()

            # Format results with proper spaces and line breaks
            if results:
                result_text = "Ingredient Analysis Results:\n\n"
                for row in results:
                    result_text += f"Ingredient Name: {row[1]}\n"
                    result_text += f"Effect: {row[2]}\n"
                    result_text += f"Affected Body Part: {row[3]}\n"
                    result_text += f"Additional Info: {row[4]}\n\n"  # Adjust column index if needed
                return f"<pre>{result_text}</pre>", 200  # Wrap in <pre> for proper HTML spacing
            else:
                return "No matching ingredients found.", 404

        except Exception as e:
            print(f"Error during processing: {e}")
            return f"Error: An error occurred while processing your request. {e}", 500
    return "Error: Invalid file format", 400



# Run the application
if __name__ == '__main__':
    app.run(debug=True)
