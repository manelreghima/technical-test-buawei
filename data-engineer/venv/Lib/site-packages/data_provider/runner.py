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

def generate_annotations(n: int, output_dir: pathlib.Path | None = None) -> pathlib.Path:
    # Dataset folder
    if output_dir is None:
        root_dir = pathlib.Path("/tmp/buawei")
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
        archive_path = generate_annotations(random.randint(1, 10))
        try:
            httpx.post(self.endpoint, files={"export": open(archive_path, "rb")})
        except Exception as e:
            print(e)
        finally:
            archive_path.unlink()
            shutil.rmtree(archive_path.with_suffix(""))

    def run(self):
        delay = self.get_random_delay()
        while True:
            time.sleep(delay / 1000.0)
            self.send()
            delay = self.get_random_delay()

