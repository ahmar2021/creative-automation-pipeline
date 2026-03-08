import os
import shutil
import random
from services.deepai_generator import DeepAIImageGenerator

def generate_image_candidates(prompt, output_prefix, n=4, use_deepai=False):
    """Lambda-ready function to generate multiple candidate images"""
    images = []
    
    if use_deepai:
        # Use DeepAI real image generation
        generator = DeepAIImageGenerator(headless=True)
        try:
            output_path = f"{output_prefix}_candidate_0.png"
            result = generator.generate_image(prompt, output_path)
            if result:
                images.append(result)
                print(f"  Generated with DeepAI")
        finally:
            generator.close()
    else:
        # Use mock images from mock_generated folder
        mock_dir = "input_assets/mock_generated"
        
        if os.path.exists(mock_dir):
            mock_files = [f for f in os.listdir(mock_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
            
            if mock_files:
                selected_mock = random.choice(mock_files)
                mock_path = os.path.join(mock_dir, selected_mock)
                output_path = f"{output_prefix}_candidate_0.png"
                
                shutil.copy(mock_path, output_path)
                images.append(output_path)
                
                print(f"  Using mock image: {selected_mock}")
        else:
            print(f"Warning: No mock images found in {mock_dir}")
    
    return images

def lambda_handler(event, context):
    """AWS Lambda handler"""
    prompt = event.get("prompt")
    output_prefix = event.get("output_prefix")
    n = event.get("n", 4)
    
    images = generate_image_candidates(prompt, output_prefix, n)
    
    return {
        "statusCode": 200,
        "body": {"images": images}
    }
