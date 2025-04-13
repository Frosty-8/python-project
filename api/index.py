from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload and cleaned data folders
UPLOAD_FOLDER = 'uploads'
CLEANED_FOLDER = 'cleaned'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CLEANED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    df = pd.read_csv(filepath)
    preview = df.head().to_html(classes='table table-striped table-bordered', index=False)

    return render_template('preview.html', preview=preview, filename=filename, cleaned_preview=None)

@app.route('/clean_all/<filename>', methods=['POST'])
def clean_all(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # Read original data
    df_raw = pd.read_csv(filepath)

    # Perform cleaning
    df_cleaned = df_raw.drop_duplicates()
    df_cleaned = df_cleaned.fillna(method='ffill')

    # Save cleaned file
    cleaned_filename = f"cleaned_{filename}"
    cleaned_path = os.path.join(CLEANED_FOLDER, cleaned_filename)
    df_cleaned.to_csv(cleaned_path, index=False)

    # Previews
    raw_preview = df_raw.head().to_html(classes='table table-striped table-bordered', index=False)
    cleaned_preview = df_cleaned.head().to_html(classes='table table-striped table-bordered', index=False)

    return render_template('preview.html',
                           preview=raw_preview,
                           cleaned_preview=cleaned_preview,
                           filename=filename,
                           cleaned_filename=cleaned_filename)

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(CLEANED_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

# if __name__ == '__main__':
#     app.run(debug=True)