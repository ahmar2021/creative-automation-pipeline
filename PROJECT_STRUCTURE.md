# Project Structure

```
creative-automation-pipeline/
├── brands/
│   ├── hydralife/
│   │   └── brand_guidelines.json
│   ├── fitlife/
│   │   └── brand_guidelines.json
│   ├── ecohome/
│   │   └── brand_guidelines.json
│   ├── luxebeauty/
│   │   └── brand_guidelines.json
│   └── techgear/
│       └── brand_guidelines.json
│
├── briefs/
│   ├── hydralife_campaign.json
│   ├── fitlife_campaign.json
│   ├── ecohome_campaign.json
│   ├── luxebeauty_campaign.json
│   └── techgear_campaign.json
│
├── input_assets/
│   ├── hydralife/
│   │   ├── hydraboost.jpg
│   │   └── logo.jpeg
│   ├── luxebeauty/
│   │   ├── GlowSerum Pro/
│   │   │   ├── 1x1.jpeg
│   │   │   ├── 9x16.jpeg
│   │   │   └── 16x9.jpeg
│   │   └── LuxeLash Mascara/
│   │       ├── 1x1.jpeg
│   │       ├── 9x16.jpeg
│   │       └── 16x9.jpeg
│   └── mock_generated/
│       └── *.jpeg
│
├── services/
│   ├── asset_service.py
│   ├── creative_composer_service.py
│   ├── creative_scoring_service.py
│   ├── deepai_generator.py
│   ├── image_generator_service.py
│   ├── image_processor_service.py
│   ├── legal_check_service.py
│   └── storage_service.py
│
├── utils/
│   ├── config.py
│   └── prompt_builder.py
│
├── output/
│   └── {brand_id}_{Campaign}_{Timestamp}/
│       ├── {Product_1}/
│       │   ├── 1x1.jpg
│       │   ├── 9x16.jpg
│       │   └── 16x9.jpg
│       └── {Product_2}/
│           ├── 1x1.jpg
│           ├── 9x16.jpg
│           └── 16x9.jpg
│
├── temp/
│
├── main.py
├── requirements.txt
├── README.md
├── API.md
├── DEPLOYMENT.md
├── MOCK_SETUP.md
└── PROJECT_STRUCTURE.md
```

## Key Directories

### brands/
Brand-specific configurations organized by brand_id.
Each brand has `brand_guidelines.json` with colors, banned words, and logo path.

### briefs/
Campaign briefs in JSON format. Products can include:
- `"asset_folder"` — subfolder name under `input_assets/{brand_id}/` with pre-made aspect ratio images
- No asset fields — triggers AI generation or mock

### input_assets/
- `{brand_id}/{product_name}/` — Pre-made aspect ratio images (1x1, 9x16, 16x9)
- `{brand_id}/` — Single product assets and logos
- `mock_generated/` — Mock images for fast testing

### output/
Generated creatives: `{brand_id}_{Campaign_Name}_{YYYYMMDD_HHMMSS}/`

### services/
Lambda-ready functions:
- `asset_service.py` — Checks for pre-made variant assets or single assets
- `deepai_generator.py` — Selenium browser automation with native shape selection
- `image_generator_service.py` — Orchestrates mock or DeepAI generation per ratio
- `image_processor_service.py` — Resizes single images into aspect ratio variants
- `creative_composer_service.py` — Text overlay + CTA button + logo
- `creative_scoring_service.py` — Mock quality scoring
- `legal_check_service.py` — Brand compliance validation
- `storage_service.py` — Brand-organized output folders

## Pipeline Priority Order

For each product:
1. **Pre-made variants** (`asset_folder`) → copies images, generates missing ratios
2. **Single asset** (`asset`) → resizes into all ratios
3. **DeepAI** (with `--deepai`) → generates 3 natively shaped images
4. **Mock** (default) → random mock image + resize

## Creative Composer

Each output image includes:
- **Text overlay**: Campaign message in a white bar (15% of image height, auto-scaling font)
- **CTA button**: "Shop now" pill button with brand's `primary_color`
- **Logo**: Top-right corner

## Aspect Ratios

- **1:1** (1080x1080) — Instagram Feed
- **9:16** (1080x1920) — TikTok/Reels/Stories
- **16:9** (1920x1080) — YouTube/Facebook

## Adding a New Brand

1. Create `brands/{brand_id}/brand_guidelines.json`
2. Create `input_assets/{brand_id}/` (add logo and optional product assets)
3. Create `briefs/{brand_id}_campaign.json`
4. Run: `python3 main.py briefs/{brand_id}_campaign.json`
