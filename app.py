import logging
logging.basicConfig(level=logging.DEBUG)
from flask import Flask, request, send_file  
from rembg import remove
from PIL import Image
import io

app = Flask(__name__)

# This route shows a welcome message when visiting the root URL.
@app.route('/')
def index():
    return "Welcome to the Background Remover API. Use the /remove-bg endpoint to remove backgrounds."

# This route handles POST requests to remove the background from an image.
@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    try:
        # Check if an image was uploaded
        if 'image' not in request.files:
            return {"error": "No image uploaded"}, 400
            
        file = request.files['image']
        if file.filename == '':
            return {"error": "Empty filename"}, 400

        # Open the image file from the upload stream.
        with Image.open(file.stream) as img:
            # Remove the background using the rembg.remove function.
            # (If you prefer to simply copy the image without processing, you can replace this line with: output = img.copy())
            output = remove(img)
            
        # Save the processed image into a BytesIO object.
        img_bytes = io.BytesIO()
        output.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        # Send the processed image back as a file download.
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
    # Use Waitress for production deployment.
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000)
