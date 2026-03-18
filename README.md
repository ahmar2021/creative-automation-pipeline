# Creative Automation Pipeline - Proof of Concept

## Overview

A serverless-ready creative automation pipeline that generates branded social ad campaigns using GenAI. Supports multiple brands with brand-specific guidelines, assets, and compliance rules. Each component is designed as an independent Lambda-deployable service.

## Architecture

```
Campaign Brief + Brand Guidelines (JSON)
        │
        ▼
API Controller (main.py)
        │
 ┌──────┴──────┬──────────┬──────────┬──────────┐
 ▼             ▼          ▼          ▼          ▼
Legal      Asset      Generator  Scoring   Processor
Check      Service    Service    Service   Service
(Brand)    (Brand)    (DeepAI)   (Mock)    (Variants)
                                              │
                                              ▼
                                          Composer
                                       (Text + CTA + Logo)
        │
        ▼
Brand-Organized Storage
```

## Features

### Core Pipeline
- **Multi-candidate generation**: Generates images per aspect ratio, scores them, selects best
- **Native shape generation**: Uses DeepAI's shape options to generate images in the correct aspect ratio (Square, Tall, Wide) instead of cropping/resizing
- **Pre-made asset support**: Products can reference a folder of pre-made aspect ratio images; missing ratios are auto-generated
- **Mock scoring**: Random quality scores (7-9.5 range) for POC; production-ready for vision model integration
- **Multi-format output**: 1:1 (Instagram), 9:16 (TikTok/Reels), 16:9 (YouTube)

### Brand Management
- **Multi-brand support**: Separate folders for each brand's assets and guidelines
- **Brand-specific compliance**: Each brand has its own banned words list
- **Brand-organized output**: Output folders named `{brand_id}_{campaign_name}_{timestamp}`
- **Logo overlay**: Automatic brand logo placement (top-right corner)
- **Text overlay**: Campaign message in a semi-transparent white bar (capped at 15% of image height)
- **CTA button**: "Shop now" button using the brand's primary color

### Image Generation Modes
- **Pre-made Assets**: Uses images from `input_assets/{brand_id}/{product_name}/` when available
- **Mock Mode (Default)**: Uses random images from `input_assets/mock_generated/` for fast testing
- **DeepAI Mode**: Real image generation using DeepAI's text2img model via Selenium browser automation with native shape selection

### Lambda-Ready Design
- Each service is independently deployable
- Stateless functions
- Event-driven architecture ready

## Quick Start

### Prerequisites

```bash
# Upgrade pip first
python3 -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Usage

```
usage: main.py [-h] [--deepai] [--zimage] [--wan] [--qwen] [--flux9b] [--flux4b] [brief]

positional arguments:
  brief       path to campaign brief JSON file (default: briefs/hydralife_campaign.json)

options:
  -h, --help  show this help message and exit
  --deepai    use DeepAI for image generation
  --zimage    use Upsampler with Z-Image Turbo
  --wan       use Upsampler with Wan 2.2 14B
  --qwen      use Upsampler with Qwen Image
  --flux9b    use Upsampler with Flux 2 Klein 9B
  --flux4b    use Upsampler with Flux 2 Klein 4B
```

### Run Pipeline

**Mock Mode with pre-made assets (LuxeBeauty):**

The LuxeBeauty brief has pre-made images for all aspect ratios in `input_assets/luxebeauty/`. No image generation needed.

```bash
python3 main.py briefs/luxebeauty_campaign.json
```

**DeepAI image generation (HydraLife):**

The HydraLife brief has no pre-made assets, so all images are generated via DeepAI. Generates 3 images per product (one per aspect ratio) using native shape selection.

```bash
python3 main.py briefs/hydralife_campaign.json --deepai
```

**Mock Mode without pre-made assets:**

Brands without pre-made assets use random mock images from `input_assets/mock_generated/`.

```bash
python3 main.py briefs/techgear_campaign.json
```

### Generation Modes Summary

| Brief | Pre-made Assets | Mock Mode | DeepAI Mode |
|-------|----------------|-----------|-------------|
| **luxebeauty** | ✓ All 3 ratios per product | N/A (assets used) | N/A (assets used) |
| **hydralife** | ✗ | Mock images | Real generation |
| **techgear** | ✗ | Mock images | Real generation |
| **fitlife** | ✗ | Mock images | Real generation |
| **ecohome** | ✗ | Mock images | Real generation |

## Input Format

### Campaign Brief

Products with pre-made assets (`briefs/luxebeauty_campaign.json`):

```json
{
  "campaign_name": "Holiday Glow Collection",
  "brand_id": "luxebeauty",
  "region": "North America",
  "audience": "Women aged 25-45",
  "message": "Radiate confidence this season",
  "products": [
    {
      "name": "GlowSerum Pro",
      "description": "Anti-aging serum with vitamin C and hyaluronic acid",
      "asset_folder": "GlowSerum Pro"
    }
  ]
}
```

Products without assets (`briefs/hydralife_campaign.json`):

```json
{
  "campaign_name": "Summer Hydration",
  "brand_id": "hydralife",
  "region": "UK",
  "audience": "Young professionals",
  "message": "Stay refreshed all summer",
  "products": [
    {
      "name": "HydraBoost Water",
      "description": "Premium electrolyte water"
    }
  ]
}
```

### Pre-made Assets Structure

When a product has `"asset_folder"`, the pipeline looks for images in:

```
input_assets/{brand_id}/{asset_folder}/
├── 1x1.jpeg     # Square (Instagram)
├── 9x16.jpeg    # Tall portrait (TikTok/Reels)
└── 16x9.jpeg    # Wide landscape (YouTube)
```

If some ratios are missing, they are auto-generated via DeepAI (with `--deepai`) or mock.

### Brand Guidelines

`brands/{brand_id}/brand_guidelines.json`:

```json
{
  "brand_name": "HydraLife",
  "brand_id": "hydralife",
  "primary_color": "#00AEEF",
  "secondary_color": "#003366",
  "logo_path": "input_assets/hydralife/logo.jpeg",
  "banned_words": ["miracle cure", "guaranteed results"]
}
```

**Available Brands:**
- `hydralife` - HydraLife Water Products
- `fitlife` - FitLife Fitness Gear
- `ecohome` - EcoHome Sustainable Products
- `luxebeauty` - LuxeBeauty Cosmetics
- `techgear` - TechGear Electronics

## Output Structure

```
output/
└── {brand_id}_{Campaign_Name}_{Timestamp}/
    ├── {Product_1}/
    │   ├── 1x1.jpg      # 1080x1080 Instagram Feed
    │   ├── 9x16.jpg     # 1080x1920 TikTok/Reels/Stories
    │   └── 16x9.jpg     # 1920x1080 YouTube/Facebook
    └── {Product_2}/
        ├── 1x1.jpg
        ├── 9x16.jpg
        └── 16x9.jpg
```

Each output image includes:
- The generated or pre-made product image
- Campaign message text overlay (bottom bar, 15% of image height)
- "Shop now" CTA button in the brand's primary color
- Brand logo (top-right corner)

## Sample Outputs

Below are sample outputs generated by the creative automation pipeline detectors across different campaigns and aspect ratios.

### FitLife — New Year Fitness Goals

| EnduroMax Pre-Workout (1x1) | PowerFlex Protein (1x1) |
|-----|------|
| <img src="https://raw.githubusercontent.com/ahmar2021/creative-automation-pipeline/main/output/fitlife_New%20Year%20Fitness%20Goals_20260309_140411/EnduroMax%20Pre-Workout/1x1.jpg" width="200"> | <img src="https://raw.githubusercontent.com/ahmar2021/creative-automation-pipeline/main/output/fitlife_New%20Year%20Fitness%20Goals_20260309_140411/PowerFlex%20Protein/1x1.jpg" width="200"> |

### HydraLife — Summer Hydration

| HydraBoost Water (1x1) |
|-----|
| <img src="https://raw.githubusercontent.com/ahmar2021/creative-automation-pipeline/main/output/hydralife_Summer%20Hydration_20260309_133335/HydraBoost%20Water/1x1.jpg" width="200"> |

### LuxeBeauty — Holiday Glow Collection

| LuxeLash Mascara (9x16) | GlowSerum Pro (9x16) | GlowSerum Pro (16x9) |
|------|------|------|
| <img src="https://raw.githubusercontent.com/ahmar2021/creative-automation-pipeline/main/output/luxebeauty_Holiday%20Glow%20Collection_20260309_125325/LuxeLash%20Mascara/9x16.jpg" width="200"> | <img src="https://raw.githubusercontent.com/ahmar2021/creative-automation-pipeline/main/output/luxebeauty_Holiday%20Glow%20Collection_20260309_125325/GlowSerum%20Pro/9x16.jpg" width="200"> | <img src="https://raw.githubusercontent.com/ahmar2021/creative-automation-pipeline/main/output/luxebeauty_Holiday%20Glow%20Collection_20260309_125325/GlowSerum%20Pro/16x9.jpg" width="200"> |

### GlossVeil — Bold Lips Summer

| Crystal Gloss Lip Oil (1x1) |
|------|
| <img src="https://raw.githubusercontent.com/ahmar2021/creative-automation-pipeline/main/output/glossveil_Bold%20Lips%20Summer_20260309_151428/Crystal%20Gloss%20Lip%20Oil/1x1.jpg" width="200"> |

## Lambda Services

### 1. Legal Check Service
**File**: `services/legal_check_service.py`
- Validates campaign message against banned words

### 2. Asset Service
**File**: `services/asset_service.py`
- Checks for pre-made aspect ratio assets in `input_assets/{brand_id}/{product_name}/`
- Checks for single existing assets
- Returns paths or triggers generation

### 3. Image Generator Service
**File**: `services/image_generator_service.py`
- Generates images per aspect ratio with native shape selection
- Supports DeepAI (real) and mock modes
- Can generate only specific missing ratios

### 4. DeepAI Generator
**File**: `services/deepai_generator.py`
- Browser automation via Selenium + Chrome
- Reuses Chrome profile cookies for authenticated access
- Native shape selection: Square (1:1), Tall (9:16), Wide (16:9)
- Polls for generated images with error detection

### 5. Creative Scoring Service
**File**: `services/creative_scoring_service.py`
- Mock random scores (7-9.5 range) for POC
- Production: GPT-4 Vision or Claude for real quality scoring

### 6. Image Processor Service
**File**: `services/image_processor_service.py`
- Creates aspect ratio variants by resizing (used for single-asset flow)

### 7. Creative Composer Service
**File**: `services/creative_composer_service.py`
- **Text overlay**: Campaign message in white bar (15% of image height, auto-scaling font)
- **CTA button**: "Shop now" pill button with brand primary color background
- **Logo overlay**: Top-right corner placement

### 8. Storage Service
**File**: `services/storage_service.py`
- Creates brand-organized output folders

## Pipeline Priority Order

For each product, the pipeline checks in this order:

1. **Pre-made variants** (`asset_folder`) → copies images, generates missing ratios
2. **Single asset** (`asset`) → resizes into all ratios
3. **DeepAI** (with `--deepai` flag) → generates 3 natively shaped images
4. **Mock** (default) → random mock image + resize

## Dependencies

```
pillow>=10.0.0
requests>=2.31.0
selenium>=4.15.0
webdriver-manager>=4.0.0
```

**System Requirements:**
- Python 3.9+
- Google Chrome (for DeepAI mode)
- macOS fonts: Futura Bold (falls back to Helvetica, Impact)

## Scaling to Enterprise

### Current (POC)
```
Local Python Script → Sequential Processing → File System Storage
```

### Production Architecture
```
API Gateway → Step Functions → Parallel Lambdas → S3 + CloudFront
```

| Component | POC | Production |
|-----------|-----|------------|
| **Orchestration** | main.py | API Gateway + Step Functions |
| **Compute** | Local functions | AWS Lambda |
| **Image Gen** | DeepAI (Selenium) | Bedrock (Stable Diffusion / Nova Canvas) |
| **Storage** | File system | S3 + CloudFront |
| **Scoring** | Mock random | GPT-4 Vision / Claude |

## License

MIT
