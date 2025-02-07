from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from rembg import remove
from fastapi.middleware.cors import CORSMiddleware
import os  # <-- Add this
import unicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
)

@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "Invalid file type")
    try:
        input_image = await file.read()
        output_image = remove(input_image)
        return Response(content=output_image, media_type="image/png")
    except Exception as e:
        raise HTTPException(500, f"Error: {str(e)}")

# Add this block to bind to Render’s PORT
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Ensures it binds to the correct port
    uvicorn.run(app, host="0.0.0.0", port=port)
