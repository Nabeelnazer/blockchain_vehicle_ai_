from ultralytics import YOLO
import yaml
import os

def create_dataset_yaml():
    dataset_config = {
        'path': '../dataset',
        'train': 'train/images',
        'val': 'valid/images',
        'names': {
            0: 'license_plate'
        }
    }
    
    with open('../dataset.yaml', 'w') as f:
        yaml.dump(dataset_config, f)

def train_model():
    model = YOLO('yolov8n.pt')
    
    results = model.train(
        data='../dataset.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        patience=50,
        save=True,
        device='0' if torch.cuda.is_available() else 'cpu',
        project='runs',
        name='train'
    )

if __name__ == "__main__":
    create_dataset_yaml()
    train_model()