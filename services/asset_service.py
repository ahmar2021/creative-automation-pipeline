import os
from utils.config import INPUT_ASSETS_DIR

def get_existing_asset(product, brand_id):
    """Lambda-ready function to check if asset exists in brand folder"""
    asset_name = product.get("asset")
    
    if not asset_name:
        return None
    
    # Look in brand-specific folder first
    brand_path = os.path.join(INPUT_ASSETS_DIR, brand_id, asset_name)
    if os.path.exists(brand_path):
        return brand_path
    
    # Fallback to root assets folder
    root_path = os.path.join(INPUT_ASSETS_DIR, asset_name)
    if os.path.exists(root_path):
        return root_path
    
    return None

def lambda_handler(event, context):
    """AWS Lambda handler"""
    product = event.get("product")
    asset_path = get_existing_asset(product)
    
    return {
        "statusCode": 200,
        "body": {"asset_path": asset_path}
    }
