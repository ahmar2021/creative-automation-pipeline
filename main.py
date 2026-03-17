import json
import os
import sys

from services.asset_service import get_existing_asset, get_existing_asset_variants
from services.image_generator_service import generate_image_candidates, generate_shaped_variants
from services.upsampler_generator import MODEL_MAP
from services.creative_scoring_service import select_best_image
from services.image_processor_service import create_variants
from services.creative_composer_service import add_text_overlay, add_logo, add_cta_button
from services.legal_check_service import validate_message
from services.storage_service import get_product_output_folder

from utils.prompt_builder import build_prompt, REQUIRED_PRODUCT_FIELDS, REQUIRED_BRIEF_FIELDS
from utils.config import TEMP_DIR, ASPECT_RATIOS

REQUIRED_BRIEF_TOP_FIELDS = ['campaign_name', 'brand_id', 'message', 'products'] + REQUIRED_BRIEF_FIELDS


def _validate_brief(brief, brief_path):
    errors = []

    missing = [f for f in REQUIRED_BRIEF_TOP_FIELDS if f not in brief]
    if missing:
        errors.append(f"  Campaign brief is missing required fields: {', '.join(missing)}")

    for i, product in enumerate(brief.get('products', [])):
        missing = [f for f in REQUIRED_PRODUCT_FIELDS if f not in product]
        if missing:
            errors.append(f"  Product #{i + 1} is missing required fields: {', '.join(missing)}")

    if errors:
        print(f"\n✗ Validation failed for '{brief_path}':")
        for e in errors:
            print(e)
        print(f"\n  Required brief fields: {', '.join(REQUIRED_BRIEF_TOP_FIELDS)}")
        print(f"  Required product fields: {', '.join(REQUIRED_PRODUCT_FIELDS)}")
        sys.exit(1)


def run_pipeline(brief_path, brand_config_path=None, use_deepai=False, upsampler_model=None):
    """
    API Controller - Orchestrates the creative automation pipeline
    In production, this becomes API Gateway + Step Functions
    """
    
    # Load campaign brief
    with open(brief_path) as f:
        brief = json.load(f)
    
    # Validate brief and product fields early
    _validate_brief(brief, brief_path)
    
    # Load brand guidelines based on brand_id from brief
    brand_id = brief.get("brand_id")
    if not brand_id:
        raise ValueError("Campaign brief must include 'brand_id'")
    
    if not brand_config_path:
        brand_config_path = f"brands/{brand_id}/brand_guidelines.json"
    
    with open(brand_config_path) as f:
        brand_config = json.load(f)
    
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Create single timestamp for this pipeline run
    from datetime import datetime
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print(f"\n{'='*60}")
    print(f"Campaign: {brief['campaign_name']}")
    print(f"Run ID: {run_timestamp}")
    gen_label = 'DeepAI (Real)' if use_deepai else f'Upsampler ({MODEL_MAP[upsampler_model]})' if upsampler_model else 'Mock'
    print(f"Image Generation: {gen_label}")
    print(f"{'='*60}\n")
    
    # Legal compliance check (Lambda 1)
    print("Running brand compliance checks...")
    try:
        validate_message(brief["message"], brand_config["banned_words"])
        print("✓ Legal check passed\n")
    except ValueError as e:
        print(f"✗ Legal check failed: {e}\n")
        return
    
    # Process each product
    for product in brief["products"]:
        print(f"\n{'─'*60}")
        print(f"Processing: {product['name']}")
        print(f"{'─'*60}")
        
        # Asset Service (Lambda 2)
        asset = get_existing_asset(product, brief["brand_id"])
        asset_variants = get_existing_asset_variants(product, brief["brand_id"])
        
        # Storage Service (Lambda 5)
        output_folder = get_product_output_folder(product["name"], brief["campaign_name"], run_timestamp, brief["brand_id"])

        if asset_variants:
            # Pre-made aspect ratio assets — copy to output
            import shutil
            os.makedirs(output_folder, exist_ok=True)
            variants = []
            for ratio, src_path in asset_variants.items():
                dst_path = os.path.join(output_folder, f"{ratio}.jpg")
                shutil.copy2(src_path, dst_path)
                variants.append(dst_path)
            print(f"✓ Using pre-made assets from: {product.get('asset_folder')}")
            print(f"  Loaded {len(variants)} variants")

            # Generate missing ratios
            missing = [r for r in ASPECT_RATIOS if r not in asset_variants]
            if missing:
                print(f"✓ Generating missing ratios: {', '.join(missing)}")
                prompt = build_prompt(product, brief)
                generated = generate_shaped_variants(prompt, output_folder, use_deepai=use_deepai, upsampler_model=upsampler_model, ratios=missing)
                variants.extend(generated.values())
                print(f"  Generated {len(generated)} additional variants")
        elif asset:
            hero_image = asset
            print(f"✓ Using existing asset: {asset}")
            # Resize existing asset into variants
            print("✓ Creating aspect ratio variants...")
            variants = create_variants(hero_image, output_folder)
            print(f"  Created {len(variants)} variants")
        elif use_deepai or upsampler_model:
            # Generate natively shaped images (one per aspect ratio)
            method = 'DeepAI' if use_deepai else f'Upsampler ({MODEL_MAP[upsampler_model]})'
            print(f"✓ Generating shaped images with {method}...")
            prompt = build_prompt(product, brief)
            shaped = generate_shaped_variants(prompt, output_folder, use_deepai=use_deepai, upsampler_model=upsampler_model)
            variants = list(shaped.values())
            print(f"  Generated {len(variants)} shaped variants")
        else:
            # Mock flow: generate single image, score, then resize
            print("✓ Generating new images with GenAI...")
            prompt = build_prompt(product, brief)
            output_prefix = os.path.join(TEMP_DIR, product['name'].replace(' ', '_'))
            candidates = generate_image_candidates(prompt, output_prefix, n=4, use_deepai=False)
            print(f"  Generated {len(candidates)} candidate images")

            print("✓ Scoring images with vision model...")
            hero_image, score = select_best_image(candidates, brief)
            print(f"  Best image score: {score}/10")

            print("✓ Creating aspect ratio variants...")
            variants = create_variants(hero_image, output_folder)
            print(f"  Created {len(variants)} variants")
        
        # Creative Composer Service (Lambda 7)
        print("✓ Adding brand elements...")
        for img in variants:
            add_text_overlay(img, brief["message"], brand_config["primary_color"])
            add_cta_button(img, brand_config["primary_color"])
            add_logo(img, brand_config["logo_path"])
        
        print(f"✓ Saved to: {output_folder}")
    
    print(f"\n{'='*60}")
    print("Pipeline completed successfully!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Creative Automation Pipeline - Generate ad creatives from campaign briefs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  python3 main.py briefs/hydralife_campaign.json
  python3 main.py briefs/hydralife_campaign.json --deepai
  python3 main.py briefs/glossveil_campaign.json --flux4b
""")
    parser.add_argument("brief", nargs="?", default="briefs/hydralife_campaign.json",
                        help="path to campaign brief JSON file (default: briefs/hydralife_campaign.json)")
    parser.add_argument("--deepai", action="store_true",
                        help="use DeepAI for image generation")
    model_group = parser.add_mutually_exclusive_group()
    for key, label in MODEL_MAP.items():
        model_group.add_argument(f"--{key}", action="store_true", help=f"use Upsampler with {label}")

    args = parser.parse_args()

    upsampler_model = next((k for k in MODEL_MAP if getattr(args, k)), None)

    if not args.deepai and not upsampler_model:
        print("\n🎭 Using mock images (add --deepai or a model flag for real generation)\n")

    run_pipeline(args.brief, use_deepai=args.deepai, upsampler_model=upsampler_model)
