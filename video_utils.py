import cv2, PIL, numpy as np
from PIL import Image, ImageDraw, ImageFont

def PutText(img, text, size=32):
    test_img = Image.fromarray(img)
    draw = ImageDraw.Draw(test_img)
    font = ImageFont.truetype("Roboto-Regular.ttf", size)
    draw.text((test_img.width / 2 - ((len(text) / 2) * (size / 2)), test_img.height - (15 * (size / 8))), text, font=font, align="center")
    return np.asarray(test_img)
