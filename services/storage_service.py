import os
from utils.config import OUTPUT_DIR

def get_product_output_folder(product_name, campaign_name=None, run_timestamp=None, brand_id=None):
    """Lambda-ready function to get/create product output folder with timestamp"""
    
    if brand_id and campaign_name and run_timestamp:
        base_path = os.path.join(OUTPUT_DIR, f"{brand_id}_{campaign_name}_{run_timestamp}")
    elif campaign_name and run_timestamp:
        base_path = os.path.join(OUTPUT_DIR, f"{campaign_name}_{run_timestamp}")
    elif run_timestamp:
        base_path = os.path.join(OUTPUT_DIR, run_timestamp)
    else:
        base_path = OUTPUT_DIR
    
    path = os.path.join(base_path, product_name)
    os.makedirs(path, exist_ok=True)
    
    return path

def lambda_handler(event, context):
    """AWS Lambda handler"""
    product_name = event.get("product_name")
    folder = get_product_output_folder(product_name)
    
    return {
        "statusCode": 200,
        "body": {"folder": folder}
    }
