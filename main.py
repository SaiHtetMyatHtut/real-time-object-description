from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from services.phi3vision import Phi3Vision
from services.florance2detector import Florance2Detector
from fastapi.responses import FileResponse
from fastapi import HTTPException
import io
from PIL import Image
import time
import os
import json
import shutil

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


@app.post("/detect")
async def detect_objects(image: UploadFile = File(...)):
    start_time = time.time()

    contents = await image.read()
    original_image = Image.open(io.BytesIO(contents))
    
    try:
        # Delete existing images in the output directory
        for filename in os.listdir("out/images"):
            file_path = os.path.join("out/images", filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)

        # Initialize Florance2Detector
        detector = Florance2Detector()
        
        # Process the image directly
        result = detector.detect_objects(original_image)
        print(result)
        # Generate timestamp for unique filenames
        timestamp = int(time.time())
        image_format = original_image.format.lower()

        # Save the original image
        original_filename = f"image-{timestamp}.{image_format}"
        original_image.save(f"out/images/{original_filename}")

        # Prepare data for JSON
        json_data = [{
            "image": original_filename,
            "description": "original image"
        }]

        # Process detected objects
        detected_objects = []
        for i, (bbox, label) in enumerate(zip(result["<DENSE_REGION_CAPTION>"]["bboxes"], result["<DENSE_REGION_CAPTION>"]["labels"])):
            left, top, right, bottom = map(int, bbox)
            
            # Crop the detected object
            cropped_image = original_image.crop((left, top, right, bottom))
            
            # Save the cropped image
            cropped_filename = f"image-{timestamp}-{i}.{image_format}"
            cropped_image.save(f"out/images/{cropped_filename}")
            
            detected_object = {
                "label": label,
                "bbox": [left, top, right, bottom],
                "cropped_image": cropped_filename
            }
            detected_objects.append(detected_object)

            # Create JSON entry for each detected object
            object_json_data = {
                "image": cropped_filename,
                "description": label,
                "bbox": [left, top, right, bottom]
            }
            json_data.append(object_json_data)

        # Save all JSON data at once
        with open("out/out.json", "w") as json_file:
            json.dump(json_data, json_file, indent=4)

    except Exception as e:
        return {"error": str(e)}
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    return {
        "detected_objects": detected_objects,
        "processing_time": processing_time,
        "original_image": original_filename
    }

@app.get("/download/{image_name}")
async def download_image(image_name: str):
    image_path = f"out/images/{image_name}"
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/jpeg", filename=image_name)
    else:
        raise HTTPException(status_code=404, detail="Image not found")

@app.post("/save_image")
async def save_image(file: UploadFile = File(...)):
    start_time = time.time()
    
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Generate timestamp and save the image
    timestamp = int(time.time())
    image_format = image.format.lower()
    original_filename = f"image-{timestamp}.{image_format}"
    image_path = f"cout/images/{original_filename}"
    image.save(image_path)
    
    # Process the image with phi3vision
    try:
        result = phi3.process_image(image_path, "Describe this image")
        
        # Append the new entry to out.json
        json_entry = {
            "image": original_filename,
            "description": result  # Assuming result is a string description
        }
        
        try:
            with open("cout/cout.json", "r+") as json_file:
                data = json.load(json_file)
                data.append(json_entry)
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
        except FileNotFoundError:
            with open("cout/cout.json", "w") as json_file:
                json.dump([json_entry], json_file, indent=4)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        return {
            "message": "Image saved and processed successfully",
            "filename": original_filename,
            "description": result,
            "processing_time": processing_time
        }
    except Exception as e:
        return {"error": str(e)}
