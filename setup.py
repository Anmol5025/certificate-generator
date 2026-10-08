import urllib.request
import os
from PIL import Image, ImageDraw

# Create template image
img = Image.new('RGB', (800, 600), color=(255, 255, 255))
d = ImageDraw.Draw(img)
d.rectangle([20, 20, 780, 580], outline=(0, 0, 0), width=5)
img.save('assets/template.png')

# Download font
font_url = 'https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf'
urllib.request.urlretrieve(font_url, 'assets/Roboto-Regular.ttf')
