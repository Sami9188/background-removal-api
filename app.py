from flask import Flask, request, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io
import ffmpeg
import zipfile
import os
from pydub import AudioSegment
import subprocess

app = Flask(__name__)
CORS(app)  # Allow all CORS requests

@app.route('/')
def index():
    return "Welcome to the Background Remover and File Conversion API. Use the /remove-bg and /convert endpoint."

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    try:
        if 'image' not in request.files:
            return {"error": "No image uploaded"}, 400

        file = request.files['image']
        if file.filename == '':
            return {"error": "Empty filename"}, 400

        # Process image with rembg
        with Image.open(file.stream) as img:
            output = remove(img)  # Background removal happens here

        img_bytes = io.BytesIO()
        output.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        return send_file(
            img_bytes,
            mimetype='image/png',
            as_attachment=True,
            download_name='background_removed.png'
        )

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return {"error": "Internal server error"}, 500

# Convert video (MP4 -> MP3)
@app.route('/convert-video', methods=['POST'])
def convert_video():
    try:
        if 'video' not in request.files:
            return {"error": "No video uploaded"}, 400

        file = request.files['video']
        if file.filename == '':
            return {"error": "Empty filename"}, 400

        input_path = f'./uploads/{file.filename}'
        output_path = f'./uploads/{file.filename.split(".")[0]}.mp3'
        file.save(input_path)

        # Convert video to audio using FFmpeg
        ffmpeg.input(input_path).output(output_path).run()

        return send_file(output_path, as_attachment=True, download_name=f"{file.filename.split('.')[0]}.mp3")

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return {"error": "Internal server error"}, 500

# Convert audio (WAV -> MP3)
@app.route('/convert-audio', methods=['POST'])
def convert_audio():
    try:
        if 'audio' not in request.files:
            return {"error": "No audio uploaded"}, 400

        file = request.files['audio']
        if file.filename == '':
            return {"error": "Empty filename"}, 400

        input_path = f'./uploads/{file.filename}'
        output_path = f'./uploads/{file.filename.split(".")[0]}.mp3'
        file.save(input_path)

        # Convert audio to MP3 using pydub
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format="mp3")

        return send_file(output_path, as_attachment=True, download_name=f"{file.filename.split('.')[0]}.mp3")

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return {"error": "Internal server error"}, 500

# Convert document (DOCX -> PDF)
@app.route('/convert-doc', methods=['POST'])
def convert_doc():
    try:
        if 'document' not in request.files:
            return {"error": "No document uploaded"}, 400

        file = request.files['document']
        if file.filename == '':
            return {"error": "Empty filename"}, 400

        input_path = f'./uploads/{file.filename}'
        output_path = f'./uploads/{file.filename.split(".")[0]}.pdf'
        file.save(input_path)

        # Use LibreOffice to convert DOCX to PDF
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", input_path])

        return send_file(output_path, as_attachment=True, download_name=f"{file.filename.split('.')[0]}.pdf")

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return {"error": "Internal server error"}, 500

# Convert image (JPEG -> PNG)
@app.route('/convert-image', methods=['POST'])
def convert_image():
    try:
        if 'image' not in request.files:
            return {"error": "No image uploaded"}, 400

        file = request.files['image']
        if file.filename == '':
            return {"error": "Empty filename"}, 400

        input_path = f'./uploads/{file.filename}'
        output_path = f'./uploads/{file.filename.split(".")[0]}.png'
        file.save(input_path)

        # Convert image to PNG using PIL
        with Image.open(input_path) as img:
            img.save(output_path, format='PNG')

        return send_file(output_path, as_attachment=True, download_name=f"{file.filename.split('.')[0]}.png")

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return {"error": "Internal server error"}, 500

# Handle ZIP file extraction
@app.route('/extract-archive', methods=['POST'])
def extract_archive():
    try:
        if 'archive' not in request.files:
            return {"error": "No archive file uploaded"}, 400

        file = request.files['archive']
        if file.filename == '':
            return {"error": "Empty filename"}, 400

        # Check if the file is a zip
        if not file.filename.endswith('.zip'):
            return {"error": "Only ZIP files are supported"}, 400

        input_path = f'./uploads/{file.filename}'
        extract_dir = f'./uploads/{file.filename.split(".")[0]}_extracted/'

        # Save the uploaded file
        file.save(input_path)

        # Extract ZIP file
        with zipfile.ZipFile(input_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Return the extracted folder as a downloadable zip file
        output_zip = f'./uploads/{file.filename.split(".")[0]}_extracted.zip'
        with zipfile.ZipFile(output_zip, 'w') as zipf:
            for root, dirs, files in os.walk(extract_dir):
                for file in files:
                    zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), extract_dir))

        return send_file(output_zip, as_attachment=True, download_name=f"{file.filename.split('.')[0]}_extracted.zip")

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return {"error": "Internal server error"}, 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Turn off debug in production
