from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from services.phi3vision import Phi3Vision
import io
from PIL import Image
import time
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

phi3 = Phi3Vision("cuda-int4-rtn-block-32")

@app.get("/")
async def root():
    return {"message": "Server up"}

@app.post("/describe_image")
async def describe_image(image: UploadFile = File(...)):
    start_time = time.time()

    contents = await image.read()
    image = Image.open(io.BytesIO(contents))
    
    # Save the image temporarily
    temp_image_path = "temp_image.jpg"
    image.save(temp_image_path)
    
    try:
        # Process the image
        result = phi3.process_image(temp_image_path, "Describe this image")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    return {"description": result, "processing_time": processing_time}
