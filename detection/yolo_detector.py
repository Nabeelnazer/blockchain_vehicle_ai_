from ultralytics import YOLO

class NumberPlateDetector:
    def __init__(self, model_path='best.pt'):
        # Load YOLOv8 model
        self.model = YOLO(model_path)
        
        # Move model to GPU if available
        self.device = 'cuda' if self.model.device.type == 'cuda' else 'cpu'
        
    def detect_plates(self, frame):
        # Perform detection
        results = self.model(frame, verbose=False)[0]
        
        # Extract bounding boxes
        plates = []
        for det in results.boxes.data:  # Get boxes
            if det[-1] == 0:  # Assuming 0 is the class index for license plates
                x1, y1, x2, y2 = map(int, det[:4])
                plates.append((x1, y1, x2-x1, y2-y1))  # Convert to x,y,w,h format
                
        return plates
