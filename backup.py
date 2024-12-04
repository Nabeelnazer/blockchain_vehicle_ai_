import shutil
import os
from datetime import datetime
from ultralytics import YOLO

# Load last checkpoint
model = YOLO('runs/detect/train3/weights/last.pt')

# Resume training
results = model.train(
    resume=True,
    data='dataset.yaml',
    epochs=100
)
def backup_weights():
    try:
        # Create backup folder
        backup_dir = 'model_backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Get timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup files
        weight_files = ['best.pt', 'last.pt']
        for file in weight_files:
            source = f'runs/detect/train3/weights/{file}'
            if os.path.exists(source):
                dest = f'{backup_dir}/{file.split(".")[0]}_{timestamp}.pt'
                shutil.copy2(source, dest)
                print(f"✅ Backed up {file}")
            else:
                print(f"⚠️ {file} not found")
                
    except Exception as e:
        print(f"❌ Error during backup: {str(e)}")
        
    print("Backup process completed!")

if __name__ == "__main__":
    print("Starting backup...")
    backup_weights()