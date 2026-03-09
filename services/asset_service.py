import os
import glob
from utils.config import INPUT_ASSETS_DIR, ASPECT_RATIOS

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

def get_existing_asset_variants(product, brand_id):
    """Check if pre-made aspect ratio assets exist in a product subfolder.
    Looks in input_assets/<brand_id>/<product_name>/ for 1x1, 9x16, 16x9 files.
    Returns dict mapping ratio to file path, or None.
    """
    folder_name = product.get("asset_folder")
    if not folder_name:
        return None

    folder_path = os.path.join(INPUT_ASSETS_DIR, brand_id, folder_name)
    if not os.path.isdir(folder_path):
        return None

    variants = {}
    for ratio in ASPECT_RATIOS:
        for ext in (".jpeg", ".jpg", ".png"):
            path = os.path.join(folder_path, f"{ratio}{ext}")
            if os.path.exists(path):
                variants[ratio] = path
                break

    return variants if variants else None

def lambda_handler(event, context):
    """AWS Lambda handler"""
    product = event.get("product")
    asset_path = get_existing_asset(product)
    
    return {
        "statusCode": 200,
        "body": {"asset_path": asset_path}
    }
