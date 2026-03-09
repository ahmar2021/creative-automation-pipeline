# Mock Setup Instructions

## Pre-made Assets (LuxeBeauty)

LuxeBeauty has pre-made images for all aspect ratios per product. No image generation needed.

```
input_assets/luxebeauty/
├── GlowSerum Pro/
│   ├── 1x1.jpeg
│   ├── 9x16.jpeg
│   └── 16x9.jpeg
└── LuxeLash Mascara/
    ├── 1x1.jpeg
    ├── 9x16.jpeg
    └── 16x9.jpeg
```

Run:
```bash
python3 main.py briefs/luxebeauty_campaign.json
```

## Mock Generated Images (Other Brands)

Brands without pre-made assets use random images from `input_assets/mock_generated/`.

```bash
python3 main.py briefs/hydralife_campaign.json
python3 main.py briefs/techgear_campaign.json
```

## Adding Pre-made Assets for a New Product

1. Create a folder under `input_assets/{brand_id}/{product_name}/`
2. Add images named `1x1.jpeg`, `9x16.jpeg`, `16x9.jpeg` (any of `.jpeg`, `.jpg`, `.png`)
3. Add `"asset_folder": "Product Name"` to the product in the campaign brief
4. Missing ratios are auto-generated via mock or DeepAI

## Current Setup
- ✓ Pre-made assets used when `asset_folder` is set in the brief
- ✓ Missing ratios auto-generated (mock or DeepAI)
- ✓ Mock images from `input_assets/mock_generated/` for brands without assets
- ✓ Scoring service uses mock scores (no API calls)
- ✓ Text overlay, CTA button, and logo applied to all variants
