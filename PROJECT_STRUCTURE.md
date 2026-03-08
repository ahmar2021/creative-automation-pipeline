# Project Structure

```
creative-automation-poc/
├── brands/
│   ├── hydralife/
│   │   ├── brand_guidelines.json
│   │   └── logo.png
│   ├── fitlife/
│   ├── ecohome/
│   ├── luxebeauty/
│   └── techgear/
│
├── briefs/
│   ├── hydralife_campaign.json
│   ├── fitlife_campaign.json
│   ├── ecohome_campaign.json
│   ├── luxebeauty_campaign.json
│   └── techgear_campaign.json
│
├── input_assets/
│   ├── hydralife/              # Brand-specific existing assets
│   ├── fitlife/
│   ├── ecohome/
│   ├── luxebeauty/
│   ├── techgear/
│   └── mock_generated/         # Mock images for testing
│       └── *.jpg
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
│       │   ├── 1x1.png
│       │   ├── 9x16.png
│       │   └── 16x9.png
│       └── {Product_2}/
│           ├── 1x1.png
│           ├── 9x16.png
│           └── 16x9.png
│
├── temp/
│
├── main.py
├── requirements.txt
├── README.md
├── PROJECT_STRUCTURE.md
├── MOCK_SETUP.md
└── DEPLOYMENT.md
```

## Key Directories

### brands/
Contains brand-specific configurations organized by brand_id.
Each brand has its own folder with:
- `brand_guidelines.json` - Brand colors, banned words, logo path
- `logo.png` - Brand logo for overlay

**Available Brands**: hydralife, fitlife, ecohome, luxebeauty, techgear

### briefs/
Campaign briefs in JSON format. Each brief must include:
- `brand_id` - References brand in brands/ folder
- `campaign_name` - Used in output folder naming
- `message` - Text overlay content
- `products` - Array of products to generate creatives for

### input_assets/
Assets organized by brand_id:
- `{brand_id}/` - Brand-specific existing product images
- `mock_generated/` - Mock images for fast testing (no API calls)

### output/
Generated creatives organized by brand, campaign, and timestamp.
Format: `{brand_id}_{Campaign_Name}_{YYYYMMDD_HHMMSS}/`

Example: `ecohome_Sustainable_Living_20260305_164155/`

### services/
Lambda-ready functions, each independently deployable:
- `legal_check_service.py` - Brand compliance validation
- `asset_service.py` - Checks for existing brand assets
- `image_generator_service.py` - Mock or DeepAI generation
- `deepai_generator.py` - Selenium browser automation
- `creative_scoring_service.py` - Mock quality scoring
- `image_processor_service.py` - Aspect ratio variants
- `creative_composer_service.py` - Text overlay + logo
- `storage_service.py` - Brand-organized output folders

## Adding a New Brand

1. Create brand folder: `brands/{brand_id}/`
2. Add `brand_guidelines.json`:
   ```json
   {
     "brand_name": "MyBrand",
     "brand_id": "mybrand",
     "primary_color": "#FF5733",
     "secondary_color": "#C70039",
     "logo_path": "brands/mybrand/logo.png",
     "banned_words": ["cheap", "fake"]
   }
   ```
3. Add logo: `brands/{brand_id}/logo.png`
4. Create asset folder: `input_assets/{brand_id}/`
5. Create campaign brief: `briefs/{brand_id}_campaign.json`
6. Run: `python3 main.py briefs/{brand_id}_campaign.json`

## Text Overlay Styling

- **Font**: Futura Bold 80px (fallback: Futura, Montserrat, Impact, Helvetica)
- **Background**: Semi-transparent white (70% opacity, RGB 255,255,255,179)
- **Text Color**: Black, centered horizontally
- **Padding**: 30px top, 60px total bottom
- **Width**: Full image width, extends to bottom edge

## Aspect Ratios

- **1:1** (1080x1080) - Instagram Feed
- **9:16** (1080x1920) - TikTok/Reels/Stories
- **16:9** (1920x1080) - YouTube/Facebook
