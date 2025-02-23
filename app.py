from flask import Flask, request, send_file
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)
CORS(app)  # Allow all CORS requests

@app.route('/')
def index():
    return "Welcome to the Background Remover API. Use the /remove-bg endpoint. v2"

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
            output = remove(img)  # <-- Background removal happens here

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # Turn off debug in production
