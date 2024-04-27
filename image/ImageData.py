import json
from dataclasses import dataclass
from json import JSONEncoder, dumps
import numpy as np


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


@dataclass
class Image:
    image: np.ndarray
    height: int
    width: int
    status: int

    def to_json(self):
        jstr = "{"
        jstr += f"\"status\":{self.status},"
        jstr += f"\"height\":{self.height},"
        jstr += f"\"width\":{self.width},"
        jstr += f"\"image\":{self.image.tolist()}"
        # jstr += json.dumps(self.image, cls=NumpyArrayEncoder)
        jstr += "}"

        return jstr
