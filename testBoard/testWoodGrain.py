import numpy as np
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PIL import Image
import math

# Function to generate the wave-like wood texture based on the idea
def generate_wood_texture(width, height, n_points):
    # Generate random points on the surface
    points = np.random.rand(n_points, 2) * [width, height]
    
    # Initialize the image
    image = np.zeros((height, width), dtype=np.float32)
    
    # Calculate the sum of exponential decays for each point (x, y)
    for x in range(width):
        for y in range(height):
            if x%20 == 0: print(x,y)
            h = 0
            for (px, py) in points:
                dist = np.sqrt((x - px)**2 + (y - py)**2)
                h += np.exp(-dist)  # Exponential decay based on distance
            image[y, x] = h
    
    # Normalize the intensity by dividing by the number of points
    image /= n_points
    
    # Normalize the image values to the range [0, 255]
    image = np.clip(image * 255, 0, 255).astype(np.uint8)
    
    # Convert the numpy array to a PIL Image
    pil_image = Image.fromarray(image)

    return pil_image

def main():
    app = QApplication([])

    window = QWidget()
    label = QLabel(window)

    # Set the size of the image and number of random points
    width, height = 400, 300
    n_points = 50

    # Generate the wood texture
    pil_image = generate_wood_texture(width, height, n_points)
    
    # Convert the PIL image to QPixmap for use in PyQt6
    pixmap = QPixmap.fromImage(QImage(pil_image.tobytes(), width, height, pil_image.width * 3, QImage.Format.Format_RGB888))
    label.setPixmap(pixmap)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    window.setWindowTitle("Generated Wood Texture")
    window.show()

    app.exec()

if __name__ == "__main__":
    main()
