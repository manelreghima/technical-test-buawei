from fastapi import FastAPI, HTTPException, Query,File, UploadFile
import json
from fastapi.responses import JSONResponse
import shutil
import os
import zipfile
from datetime import datetime
from pathlib import Path

app = FastAPI()

# Load the annotations from coco_format.json at startup
with open('coco_format.json') as f:
    data = json.load(f)

@app.get("/search/{dataset_id}/annotations")
async def search_annotations(
    dataset_id: int,
    min_width: int = Query(100, alias="minWidth"),  # Alias to match query parameter naming conventions if needed
    max_width: int = Query(1000, alias="maxWidth")  # Alias to match query parameter naming conventions if needed
):
    # Filter annotations by dataset_id, min_width, and max_width
    filtered_annotations = [
        anno for anno in data["annotations"]
        if anno["image_id"] == dataset_id and min_width <= anno["bbox"][2] <= max_width
    ]

    if not filtered_annotations:
        raise HTTPException(status_code=404, detail="Annotations not found for the given dataset ID with specified width constraints")

    # Now get the unique image IDs from these annotations
    image_ids = {anno["image_id"] for anno in filtered_annotations}

    # Get corresponding image data
    images = [img for img in data["images"] if img["id"] in image_ids]

    # Get corresponding category data
    category_ids = {anno["category_id"] for anno in filtered_annotations}
    categories = [cat for cat in data["categories"] if cat["id"] in category_ids]

    # Prepare the response data structure
    response_data = {
        "images": images,
        "annotations": filtered_annotations,
        "categories": categories
    }

    return response_data

IMAGES_DIR = Path("./data_continuous_mode/images")
ANNOTATIONS_DIR = Path("./data_continuous_mode/annotations")

# Ensure the directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
ANNOTATIONS_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded zip file to a temporary location
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        temp_file_path = ANNOTATIONS_DIR / f"temp-{timestamp}.zip"
        with open(temp_file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Unzip the file
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(ANNOTATIONS_DIR)

            # Process each file in the archive
            for file_info in zip_ref.infolist():
                file_path = Path(file_info.filename)  # Convert to Path object to handle paths
                if file_path.suffix.lower() == '.jpg':
                    # Create the directory structure within IMAGES_DIR if not exists
                    image_dir = IMAGES_DIR / file_path.parent
                    image_dir.mkdir(parents=True, exist_ok=True)
                    # Move image to IMAGES_DIR
                    source = ANNOTATIONS_DIR / file_info.filename
                    destination = image_dir / file_path.name
                    shutil.move(str(source), str(destination))
                elif file_path.suffix.lower() == '.xml':
                    # Process annotation file (XML)
                    # For now, we just leave it in the ANNOTATIONS_DIR
                    pass
                # Add more conditions if there are other file types

        # Delete the temporary zip file
        os.remove(temp_file_path)

        return JSONResponse(status_code=200, content={"message": "File uploaded and processed successfully"})

    except Exception as e:
        # If anything goes wrong, return an error message
        print(f"An error occurred: {e}")
        return JSONResponse(status_code=500, content={"message": f"An error occurred: {e}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
