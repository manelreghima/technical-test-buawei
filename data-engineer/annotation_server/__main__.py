from fastapi import FastAPI, HTTPException, Query
import json

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
