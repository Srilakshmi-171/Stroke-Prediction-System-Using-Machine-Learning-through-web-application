"""
Create a placeholder heatmap image
"""

import numpy as np
import cv2
import os

def create_placeholder_heatmap():
    """Create a placeholder heatmap image"""
    
    # Create a gradient image
    img = np.zeros((224, 224, 3), dtype=np.uint8)
    
    # Create a gradient from blue to red
    for i in range(224):
        for j in range(224):
            # Create a circular pattern
            dist = np.sqrt((i-112)**2 + (j-112)**2)
            if dist < 80:
                val = int(255 * (1 - dist/80))
                img[i, j] = [val, 0, 255-val]  # Blue to red
            else:
                img[i, j] = [0, 0, 0]  # Black background
    
    # Add some random spots
    for _ in range(10):
        x = np.random.randint(50, 174)
        y = np.random.randint(50, 174)
        cv2.circle(img, (x, y), 10, (0, 255, 0), -1)
    
    # Save the image
    os.makedirs('static/heatmaps', exist_ok=True)
    cv2.imwrite('static/heatmaps/placeholder.png', img)
    print("Placeholder heatmap created")

if __name__ == "__main__":
    create_placeholder_heatmap()