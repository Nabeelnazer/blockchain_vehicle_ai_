import xml.etree.ElementTree as ET
import glob
import os

# Use absolute paths
base_dir = os.path.dirname(os.path.abspath(__file__))
xml_dir = os.path.join(base_dir, "xml_files")
output_dir = os.path.join(base_dir, "dataset", "train", "labels")

# Create directories if they don't exist
os.makedirs(xml_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

print(f"XML directory: {xml_dir}")
print(f"Output directory: {output_dir}")

def convert_xml_to_yolo(xml_file, output_dir):
    print(f"Processing: {xml_file}")
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    size = root.find('size')
    width = float(size.find('width').text)
    height = float(size.find('height').text)
    
    image_name = os.path.splitext(os.path.basename(xml_file))[0]
    out_file = open(os.path.join(output_dir, f"{image_name}.txt"), 'w')
    print(f"Creating: {image_name}.txt")
    
    count = 0
    for obj in root.findall('object'):
        bbox = obj.find('bndbox')
        xmin = float(bbox.find('xmin').text)
        ymin = float(bbox.find('ymin').text)
        xmax = float(bbox.find('xmax').text)
        ymax = float(bbox.find('ymax').text)
        
        # Convert to YOLO format
        x_center = (xmin + xmax) / (2.0 * width)
        y_center = (ymin + ymax) / (2.0 * height)
        box_width = (xmax - xmin) / width
        box_height = (ymax - ymin) / height
        
        out_file.write(f"0 {x_center} {y_center} {box_width} {box_height}\n")
        count += 1
    
    print(f"Converted {count} objects")
    out_file.close()

# Usage
xml_dir = "xml_files"  # folder with your XML files
output_dir = "dataset/train/labels"  # where to save converted labels

# Check directories
if not os.path.exists(xml_dir):
    print(f"Error: XML directory '{xml_dir}' not found!")
    exit()

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created output directory: {output_dir}")

for xml_file in glob.glob(os.path.join(xml_dir, "*.xml")):
    convert_xml_to_yolo(xml_file, output_dir)