# main.py
import xml.etree.ElementTree as ET
import json
import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from zipfile import ZipFile

app = FastAPI()

def voc_to_coco(voc_dir, output_file):
    coco_data = {
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    # Mapping from category names to category ids
    category_id_map = {}
    next_category_id = 1
    
    # Get list of VOC files from the given directory
    voc_files = [f for f in os.listdir(voc_dir) if f.endswith('.xml')]
    
    # Process each VOC file
    for i, file_name in enumerate(voc_files):
        file_path = os.path.join(voc_dir, file_name)
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Extract image information
        filename = root.find('filename').text
        size = root.find('size')
        width = int(size.find('width').text)
        height = int(size.find('height').text)
        
        # Add image data to COCO format
        image_id = i + 1
        coco_data['images'].append({
            "license": 1,
            "file_name": filename,
            "height": height,
            "width": width,
            "id": image_id
        })
        
        # Extract object (annotation) information
        for obj in root.findall('object'):
            category_name = obj.find('name').text
            if category_name not in category_id_map:
                category_id_map[category_name] = next_category_id
                next_category_id += 1
                # Add category data to COCO format
                coco_data['categories'].append({
                    "supercategory": "None",
                    "id": category_id_map[category_name],
                    "name": category_name
                })
            
            category_id = category_id_map[category_name]
            bbox = obj.find('bndbox')
            xmin = int(bbox.find('xmin').text)
            ymin = int(bbox.find('ymin').text)
            xmax = int(bbox.find('xmax').text)
            ymax = int(bbox.find('ymax').text)
            width = xmax - xmin
            height = ymax - ymin
            
            # Check if width and height are positive
            if width > 0 and height > 0:
                area = width * height
                
                # Add annotation data to COCO format
                coco_data['annotations'].append({
                    "segmentation": [],
                    "area": area,
                    "iscrowd": 0,
                    "image_id": image_id,
                    "bbox": [xmin, ymin, width, height],
                    "category_id": category_id,
                    "id": len(coco_data['annotations']) + 1
                })
    
    # Save COCO data to output file
    with open(output_file, 'w') as f:
        json.dump(coco_data, f, indent=2)

@app.post("/ingest-data")
async def ingest_data(file: UploadFile = File(...)):
    try:
        # Save uploaded file to temporary location
        temp_file_path = f"C:/Users/Manel/Desktop/buawei/data-engineer/temp/{file.filename}"
        with open(temp_file_path, 'wb') as f:
            f.write(file.file.read())
        
        # Unzip file and process contents
        with ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall("data")
        
        # Convert VOC to COCO format
        voc_dir = 'C:/Users/Manel/Desktop/buawei/images/5db144f2-03ab-42a8-a71c-81732847dd8a'
        output_file = 'C:/Users/Manel/Desktop/buawei/anno.json'
        voc_to_coco(voc_dir, output_file)
        
        # Delete temporary file
        os.remove(temp_file_path)
        
        return {"message": "Data ingested successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
