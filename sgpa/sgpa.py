from flask import render_template, redirect, Blueprint, request, current_app
import sgpa.conversion as conversion
import os
from werkzeug.utils import secure_filename

sgpa_bp = Blueprint("sgpa", __name__, template_folder="templates", static_folder="static")

# Set upload folders (modify paths as needed)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
CONVERTED_FOLDER = os.path.join(os.getcwd(), "converted")

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@sgpa_bp.route('/', methods=["GET", "POST"])
def main():
    try:
        if request.method == 'GET':
            return render_template("index.html")

        elif request.method == 'POST':
            convert = conversion.Conversion()

            uploaded_file = request.files['file']
            if uploaded_file and uploaded_file.filename.endswith('.pdf'):
                file_name = secure_filename(uploaded_file.filename)

                # Save the uploaded PDF file
                pdf_file = os.path.join(UPLOAD_FOLDER, file_name)
                uploaded_file.save(pdf_file)

                # Generate CSV file name and path
                first_part = file_name.rsplit('.', 1)[0]  # Get file name without extension
                csv_file = first_part + ".csv"
                csv_file_path = os.path.join(CONVERTED_FOLDER, csv_file)

                # Convert PDF to CSV and calculate SGPA
                convert.pdf_to_csv(pdf_file, csv_file_path)
                calculated_sgpa = convert.calculate(csv_file_path)
                table_data = convert.table_data(csv_file_path)

                return render_template('result.html', result=calculated_sgpa, data=table_data)

            else:
                return "Invalid file format. Please upload a PDF."

    except Exception as e:
        return f"Some error occurred! Please try again: {e}"
