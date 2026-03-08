from PIL import Image
import os
from utils.config import ASPECT_RATIOS

def create_variants(image_path, output_folder):
    """Lambda-ready function to create aspect ratio variants"""
    img = Image.open(image_path)
    
    os.makedirs(output_folder, exist_ok=True)
    
    outputs = []
    
    for ratio, size in ASPECT_RATIOS.items():
        resized = img.resize(size, Image.Resampling.LANCZOS)
        
        path = os.path.join(output_folder, f"{ratio}.jpg")
        resized.save(path, quality=95)
        
        outputs.append(path)
    
    return outputs

def lambda_handler(event, context):
    """AWS Lambda handler"""
    image_path = event.get("image_path")
    output_folder = event.get("output_folder")
    
    variants = create_variants(image_path, output_folder)
    
    return {
        "statusCode": 200,
        "body": {"variants": variants}
    }
