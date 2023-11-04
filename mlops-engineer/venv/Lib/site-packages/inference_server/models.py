import io
import pathlib

from PIL import Image
import numpy as np
import onnxruntime as ort
from PIL import Image


class Model:
    def __init__(self, path: pathlib.Path, autoload: bool = False):
        self.model: ort.InferenceSession | None = None
        self.input: str | None = None
        self.output: str | None = None

        self.path = path
        if autoload:
            self.load()

    def load(self):
        self.model = ort.InferenceSession(self.path, providers=["CPUExecutionProvider"])
        self.input = self.model.get_inputs()[0].name
        self.output = self.model.get_outputs()[0].name

    def from_bytes(self, image_bytes: bytes):
        if self.model is None:
            raise RuntimeError("Model has not been loaded")

        image = np.array(Image.open(io.BytesIO(image_bytes)))
        if image.shape[-1] == 4:
            image = image[..., :3]
        result = self.model.run(
            [self.output], {self.input: image[None, ...].astype(np.float32)}
        )
        category_id = np.argmax(result[0])
        category = f"{category_id:02d}"
        return category
