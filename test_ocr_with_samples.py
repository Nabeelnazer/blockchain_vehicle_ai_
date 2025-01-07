import cv2
from ocr.ocr import OCRStabilizer
import os
import numpy as np

# Define Kerala districts dictionary at module level
kerala_districts = {
    '01': 'Thiruvananthapuram',
    '02': 'Kollam',
    '03': 'Pathanamthitta',
    '04': 'Alappuzha',
    '05': 'Kottayam',
    '06': 'Idukki',
    '07': 'Ernakulam',
    '08': 'Thrissur',
    '09': 'Palakkad',
    '10': 'Malappuram',
    '11': 'Kozhikode',
    '12': 'Wayanad',
    '13': 'Kannur',
    '14': 'Kasaragod',
    # Additional codes for sub-RTO offices
    '15': 'Kozhikode',
    '16': 'Malappuram',
    '17': 'Ernakulam',
    '18': 'Thrissur',
    '19': 'Palakkad',
    '20': 'Thiruvananthapuram',
    '21': 'Kollam',
    '30': 'Kannur',
    '53': 'Kasaragod'
}

def test_ocr_with_samples():
    # Initialize OCR
    ocr = OCRStabilizer()
    
    # Test directory with sample images
    test_dir = 'test_samples'
    os.makedirs(test_dir, exist_ok=True)
    
    # Sample Kerala plate numbers to test
    # Format: KL-DD-XX-NNNN (DD=district code, XX=series, NNNN=number)
    sample_plates = [
        'KL01BF5544',    # Thiruvananthapuram
        'KL07CB1234',    # Kochi/Ernakulam
        'KL10MX7890',    # Palakkad
        'KL13BH6543',    # Malappuram
        'KL15FA8876',    # Kozhikode
        'KL18DC4433',    # Wayanad
        'KL05HZ2211',    # Kottayam
        'KL08AK9900',    # Thrissur
        'KL53AB1122',    # Kasaragod
        'KL30RS4455'     # Kannur
    ]
    
    # Create sample images with plate numbers
    for plate in sample_plates:
        # Create a white plate (new format in Kerala)
        img = np.zeros((200, 500, 3), np.uint8)
        img[:, :] = [255, 255, 255]  # White background
        
        # Add black border
        cv2.rectangle(img, (10, 10), (490, 190), (0, 0, 0), 2)
        
        # Split plate number for better formatting
        state_code = plate[:2]      # KL
        district_code = plate[2:4]  # District number
        series = plate[4:6]         # Series letters
        number = plate[6:]          # Registration number
        
        # Add text in black with proper spacing
        cv2.putText(img, f"{state_code} {district_code}", (30, 120),  # KL DD
                   cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 3)
        cv2.putText(img, f"{series} {number}", (200, 120),  # XX NNNN
                   cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 3)
        
        # Save sample
        cv2.imwrite(f'{test_dir}/sample_{plate}.jpg', img)
        
        # Test OCR
        detected = ocr.get_stable_plate_number(img)
        district = kerala_districts.get(district_code, 'Unknown')
        print(f"\nTesting Kerala plate {plate} ({district}):")
        print(f"Detected: {detected}")
        print(f"Match: {'✓' if detected and plate.replace(' ','') in detected else '✗'}")
        print("-" * 50)

def create_real_format_plate(text, size=(600, 140)):
    """Create a more realistic looking Kerala plate"""
    img = np.zeros((size[1], size[0], 3), np.uint8)
    img[:, :] = [255, 255, 255]  # White background (new format)
    
    # Add black border
    cv2.rectangle(img, (2, 2), (size[0]-3, size[1]-3), (0, 0, 0), 2)
    
    # Split text into components
    state_code = text[:2]      # KL
    district_code = text[2:4]  # District number
    series = text[4:6]         # Series letters
    number = text[6:]          # Registration number
    
    # Add IND hologram space (grey rectangle)
    cv2.rectangle(img, (size[0]//3, 10), (size[0]//3 + 30, size[1]-10), (128, 128, 128), -1)
    
    # Add text with proper spacing
    # State and district code
    cv2.putText(img, f"{state_code} {district_code}", (20, size[1]//2 + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    
    # Series and number
    cv2.putText(img, f"{series} {number}", (size[0]//3 + 50, size[1]//2 + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    
    return img

def test_with_realistic_plates():
    """Test OCR with more realistic looking Kerala plates"""
    ocr = OCRStabilizer()
    test_dir = 'test_samples_realistic'
    os.makedirs(test_dir, exist_ok=True)
    
    # Sample Kerala plates
    test_plates = [
        'KL07BF5544',  # Ernakulam
        'KL01AB1234',  # Thiruvananthapuram
        'KL15MX7890',  # Kozhikode
        'KL08BH6543',  # Thrissur
        'KL13FA8876',  # Malappuram
        'KL05DC4433',  # Kottayam
    ]
    
    print("\nTesting with realistic Kerala plate formats:")
    print("=" * 50)
    
    for plate in test_plates:
        # Create realistic plate image
        img = create_real_format_plate(plate)
        
        # Save the test image
        filename = f'{test_dir}/realistic_{plate}.jpg'
        cv2.imwrite(filename, img)
        
        # Test OCR
        detected = ocr.get_stable_plate_number(img)
        district_code = plate[2:4]
        district = kerala_districts.get(district_code, 'Unknown')
        print(f"\nOriginal plate: {plate} ({district})")
        print(f"Detected text:  {detected if detected else 'None'}")
        print(f"Saved image:    {filename}")
        print(f"Match:          {'✓' if detected and plate.replace(' ','') in detected else '✗'}")
        print("-" * 50)

if __name__ == "__main__":
    print("Testing with basic Kerala plate formats:")
    print("=" * 50)
    test_ocr_with_samples()
    print("\nTesting with realistic Kerala plate formats:")
    print("=" * 50)
    test_with_realistic_plates() 