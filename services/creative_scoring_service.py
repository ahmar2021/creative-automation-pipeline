import random

def score_image(image_path, brief):
    """Lambda-ready function to score image quality (MOCK MODE)"""
    # Mock scoring - return random score between 7-9
    import random
    score = random.uniform(7.0, 9.5)
    return score

import random

def select_best_image(images, brief):
    """Select the highest scoring image from candidates"""
    best_score = -1
    best_image = images[0]  # Default to first
    
    for img in images:
        score = score_image(img, brief)
        print(f"Image {img}: score {score}")
        
        if score > best_score:
            best_score = score
            best_image = img
    
    return best_image, best_score

def lambda_handler(event, context):
    """AWS Lambda handler"""
    images = event.get("images")
    brief = event.get("brief")
    
    best_image, score = select_best_image(images, brief)
    
    return {
        "statusCode": 200,
        "body": {
            "best_image": best_image,
            "score": score
        }
    }
