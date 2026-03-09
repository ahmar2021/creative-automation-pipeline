import os
import shutil
import random
from services.deepai_generator import DeepAIImageGenerator, SHAPE_MAP
from utils.config import ASPECT_RATIOS

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


def generate_shaped_variants(prompt, output_folder, use_deepai=False, ratios=None):
    """Generate one image per aspect ratio using DeepAI shape selection.
    ratios: list of ratios to generate (e.g. ['9x16']). Defaults to all.
    Returns dict mapping ratio name to image path.
    """
    os.makedirs(output_folder, exist_ok=True)
    variants = {}
    target_ratios = ratios if ratios else list(ASPECT_RATIOS.keys())

    if use_deepai:
        generator = DeepAIImageGenerator(headless=True)
        try:
            for ratio in target_ratios:
                shape = SHAPE_MAP.get(ratio)
                output_path = os.path.join(output_folder, f"{ratio}.jpg")
                print(f"  Generating asset: {ratio} aspect ratio")
                print(f"  Text prompt: {' '.join(prompt.split())}")
                result = generator.generate_image(prompt, output_path, shape=shape)
                if result:
                    variants[ratio] = result
                    print(f"  Image saved to: {output_path}")
        finally:
            generator.close()
    else:
        mock_dir = "input_assets/mock_generated"
        mock_files = [f for f in os.listdir(mock_dir) if f.endswith(('.jpg', '.png', '.jpeg'))] if os.path.exists(mock_dir) else []
        for ratio in target_ratios:
            output_path = os.path.join(output_folder, f"{ratio}.jpg")
            if mock_files:
                shutil.copy(os.path.join(mock_dir, random.choice(mock_files)), output_path)
            variants[ratio] = output_path

    return variants


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
