import cv2
import numpy as np

# Create a black image
img = np.zeros((512, 512, 3), np.uint8)

# Display the image
cv2.imshow('Test Window', img)
cv2.waitKey(0)  # Wait for a key press
cv2.destroyAllWindows()  