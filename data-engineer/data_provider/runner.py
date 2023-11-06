import pathlib
import threading
import random
import time
import httpx
from uuid import uuid4 as uuid
import shutil

object_template = """
    <object>
    <name>{category}</name>
    <pose>Unspecified</pose>
    <truncated>0</truncated>
    <difficult>0</difficult>
    <bndbox>
      <xmin>{xmin}</xmin>
      <ymin>{ymin}</ymin>
      <xmax>{xmax}</xmax>
      <ymax>{ymax}</ymax>
    </bndbox>
  </object>
"""

annotation_template = """
<annotation>
  <folder>{images_dir}</folder>
  <filename>{filename}</filename>
  <path>{path}</path>
  <source>
    <database>{dataset_id}</database>
  </source>
  <size>
    <width>900</width>
    <height>675</height>
    <depth>3</depth>
  </size>
  <segmented>0</segmented>
  {objects}
</annotation>
"""
def safe_delete(file_path, max_retries=5, delay=1.0):
    """Attempt to delete a file with retries and a delay."""
    for attempt in range(max_retries):
        try:
            file_path.unlink()
            break  # If the delete was successful, break out of the loop
        except PermissionError as e:
            if attempt < max_retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                print(f"Failed to delete file {file_path} after {max_retries} attempts.")
                raise e  # If all retries fail, re-raise the exception
                
def generate_annotations(n: int, output_dir: pathlib.Path | None = None) -> pathlib.Path:
    # Dataset folder
    if output_dir is None:
        #root_dir = pathlib.Path("/tmp/buawei")
        root_dir = pathlib.Path("./images")
        base_path = root_dir / str(uuid())
    else:
        root_dir = output_dir
        base_path = output_dir / str(uuid())

    for _ in range(n):
        dataset_id = random.randint(0, 5)
        dataset_id = f"{dataset_id:02d}"
        objects_str = ""
        for _ in range(random.randint(0, 5)):
            xmin = random.randint(0, 900)
            xmax = random.randint(0, 900)
            ymin = random.randint(0, 675)
            ymax = random.randint(0, 675)
            category_int = random.randint(0, 10)
            category = f"{category_int:02d}"
            objects_str += object_template.format(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, category=category)
    
        path = base_path / f"{str(uuid())}.jpg"
        path.parent.mkdir(exist_ok=True, parents=True)
        annotation_str = annotation_template.format(
            images_dir=str(path.parent.name),
            filename=path.name,
            path=str(path),
            dataset_id=dataset_id,
            objects=objects_str
        )
        path.touch()

        with open(path.with_suffix(".xml"), "w") as fp:
            fp.write(annotation_str)

    archive_path = shutil.make_archive(
        base_path.name,
        "zip",
        root_dir=root_dir,
        base_dir=base_path.name
    )
    archive_path = pathlib.Path(archive_path).rename(root_dir / base_path.with_suffix(".zip").name)

    return archive_path

class Runner(threading.Thread):
    
    def __init__(self, endpoint: str, min_delay: int, max_delay: int):
        super().__init__()

        self.endpoint = endpoint
        self.min_delay = min_delay
        self.max_delay = max_delay

    def get_random_delay(self):
        if self.min_delay == self.max_delay:
            return self.min_delay
        
        return random.randint(self.min_delay, self.max_delay + 1)

    


    def send(self):
        # Generate the archive with annotations
        archive_path = generate_annotations(random.randint(1, 10))
        try:
            # Send the archive to the endpoint
            with open(archive_path, "rb") as file:
                httpx.post(self.endpoint, files={"export": file})
        except Exception as e:
            print(e)
       

    def run(self):
        delay = self.get_random_delay()
        while True:
            time.sleep(delay / 1000.0)
            self.send()
            delay = self.get_random_delay()

