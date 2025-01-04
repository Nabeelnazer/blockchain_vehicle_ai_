from ultralytics import YOLO
import yaml
import os

def create_dataset_yaml():
    """Create the dataset configuration file"""
    dataset_config = {
        'path': 'dataset',  # dataset root directory
        'train': 'train/images',  
        'val': 'valid/images',    
        
        # Classes
        'names': {
            0: 'license_plate'    
        }
    }
    
    # Save dataset.yaml
    with open('dataset.yaml', 'w') as f:
        yaml.dump(dataset_config, f)

def train_model():
    """Train the YOLOv8 model"""
    # Load a pretrained YOLOv8 model
    model = YOLO('yolov8n.pt')  # you can change to s/m/l/x versions if needed
    
    # Train the model
    results = model.train(
        data='dataset.yaml',
        epochs=100,              
        imgsz=640,              
        batch=16,               
        patience=50,            
        save=True,             
        device='0',            
        workers=8,             
        project='runs',        
        name='train'           
    )

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    os.makedirs('dataset/train/images', exist_ok=True)
    os.makedirs('dataset/train/labels', exist_ok=True)
    os.makedirs('dataset/valid/images', exist_ok=True)
    os.makedirs('dataset/valid/labels', exist_ok=True)
    
    # Create dataset.yaml
    create_dataset_yaml()
    
    # Start training
    train_model() 