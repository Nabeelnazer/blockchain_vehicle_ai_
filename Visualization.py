import cv2
import matplotlib.pyplot as plt

# Read the annotated image
img = cv2.imread('prediction_result.jpg')
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.title('License Plate Detection')
plt.show()
