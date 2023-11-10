import requests
import os
from PIL import Image, ImageDraw
import numpy as np
from io import BytesIO


def image(url: str):
    response = requests.get(url)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content)).convert("RGB")

        new_size = (120, 115)
        img = img.resize(new_size)

        npImage = np.array(img)
        h, w = img.size

        alpha = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0, 0, h, w], 0, 360, fill=255)

        npAlpha = np.array(alpha)

        npImage = np.dstack((npImage, npAlpha))

        file_path = 'pfp.png'

        if os.path.exists(file_path):
            os.remove(file_path)

            Image.fromarray(npImage).save('main/utils/banner/pics/pfp.png')
        else:
            Image.fromarray(npImage).save('main/utils/banner/pics/pfp.png')
    else:
        return None
