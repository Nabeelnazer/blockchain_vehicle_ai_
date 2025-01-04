import cv2
import numpy as np

# Create a black image
img = np.zeros((512, 512, 3), np.uint8)

# Add visuals
cv2.rectangle(img, (50, 50), (300, 300), (0, 255, 0), thickness=3)  # Green rectangle
cv2.circle(img, (256, 256), 50, (0, 0, 255), -1)  # Red circle
cv2.putText(img, 'Hello, OpenCV!', (100, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)  # Text


# Display the image
cv2.imshow('Test Window', img)
cv2.waitKey(0)  # Wait for a key press
cv2.destroyAllWindows()
