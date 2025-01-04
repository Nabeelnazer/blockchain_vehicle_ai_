from ultralytics import YOLO
import os
import glob
import cv2

def find_model():
    """
    Comprehensive model finder with multiple search strategies
    """
    search_paths = [
        '.',  # Current directory
        '..',  # Parent directory
        'runs',
        '../runs',
        'runs/detect',
        '../runs/detect',
        'weights',
        '../weights'
    ]

    model_patterns = [
        '**/*.pt',   
        '**/best.pt', 
        '**/last.pt'  
    ]

    for search_path in search_paths:
        for pattern in model_patterns:
            full_pattern = os.path.join(search_path, pattern)
            models = glob.glob(full_pattern, recursive=True)
            
            if models:
                model_path = os.path.abspath(models[0])
                print(f"🤖 Model found at: {model_path}")
                return model_path

    raise FileNotFoundError("Could not find the trained YOLO model.")

def find_test_image():
    """
    Comprehensive test image finder
    """
    search_paths = [
        '.',  # Current directory
        '..',  # Parent directory
        'dataset',
        '../dataset',
        'data',
        '../data'
    ]

    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
    
    for path in search_paths:
        for ext in image_extensions:
            images = glob.glob(os.path.join(path, '**', ext), recursive=True)
            if images:
                print(f"🖼️ Test image found: {os.path.abspath(images[0])}")
                return images[0]
    
    raise FileNotFoundError("No test image found. Please provide a test image.")

def predict_license_plate():
    """
    Predict license plates in an image
    """
    # Find and load the model
    model_path = find_model()
    model = YOLO(model_path)

    # Find test image
    image_path = find_test_image()

    # Predict on the image
    results = model(image_path)

    # Visualize results
    for r in results:
        # Plot and save annotated image
        annotated_frame = r.plot()
        cv2.imwrite('prediction_result.jpg', annotated_frame)
        
        # Print detection details
        for box in r.boxes:
            class_name = r.names[box.cls[0].item()]
            confidence = box.conf[0].item()
            print(f"🚗 Detected {class_name} with confidence {confidence:.2f}")

if __name__ == "__main__":
    predict_license_plate()