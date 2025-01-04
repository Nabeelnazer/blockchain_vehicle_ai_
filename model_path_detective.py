import os
import glob

def find_model_files():
    """
    Comprehensive model file search
    """
    search_paths = [
        os.getcwd(),  # Current directory
        os.path.dirname(os.getcwd()),  # Parent directory
        'model_backups',  # Specific backup folder
        'runs',  # Training output
        'weights'  # Common weights directory
    ]

    # Search patterns
    model_patterns = [
        '**/*best*.pt',
        '**/*last*.pt',
        '**/*.pt'
    ]

    found_models = []

    for search_path in search_paths:
        for pattern in model_patterns:
            full_pattern = os.path.join(search_path, pattern)
            models = glob.glob(full_pattern, recursive=True)
            
            found_models.extend(models)

    # Print found models with clean paths
    if found_models:
        print("🤖 Found YOLO Models:")
        for model in found_models:
            try:
                clean_path = os.path.abspath(model)
                print(f"- {clean_path}")
                print(f"  Size: {os.path.getsize(clean_path)/1024/1024:.2f} MB")
            except Exception as e:
                print(f"Error processing {model}: {e}")
    else:
        print("❌ No models found. Recommendation: Retrain or download model.")

def sanitize_path(path):
    """
    Clean and sanitize file paths
    """
    # Remove non-printable characters
    return ''.join(char for char in path if char.isprintable())

if __name__ == "__main__":
    find_model_files() 