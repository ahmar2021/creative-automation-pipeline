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
                                          (Text + Logo)
        │
        ▼
Brand-Organized Storage
```

## Features

### Core Pipeline
- **Multi-candidate generation**: Generates 4 images, scores them, selects best
- **Mock scoring**: Random quality scores (7-9.5 range) for POC; production-ready for vision model integration
- **Asset reuse**: Checks brand-specific asset folders before generating new images
- **Multi-format output**: 1:1 (1080x1080 Instagram), 9:16 (1080x1920 TikTok/Reels), 16:9 (1920x1080 YouTube)

### Brand Management
- **Multi-brand support**: Separate folders for each brand's assets and guidelines
- **Brand-specific compliance**: Each brand has its own banned words list
- **Brand-organized output**: Output folders named `{brand_id}_{campaign_name}_{timestamp}`
- **Logo overlay**: Automatic brand logo placement (top-right corner)
- **Text overlay styling**: Semi-transparent white background (70% opacity), Futura Bold 80px font, black text, centered with proper padding

### Image Generation Modes
- **Mock Mode (Default)**: Uses random images from `input_assets/mock_generated/` for fast testing
- **DeepAI Mode**: Real image generation using DeepAI's text2img model via Selenium browser automation (700x700 images)

### Lambda-Ready Design
- Each service is independently deployable
- Stateless functions
- Event-driven architecture ready

## Quick Start

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run Pipeline

**Mock Mode (Default - Fast):**
```bash
python3 main.py
```

**With Specific Brief:**
```bash
python3 main.py briefs/hydralife_campaign.json
```

**Real Image Generation (DeepAI):**
```bash
python3 main.py briefs/ecohome_campaign.json --deepai
```

**Modes:**
- **Mock Mode**: Uses pre-existing mock images from `input_assets/mock_generated/` (fast, no API calls)
- **DeepAI Mode**: Generates real images using DeepAI's text2img model via Selenium browser automation
  - Navigates to deepai.org/machine-learning-model/text2img
  - Enters prompt and triggers generation via Enter key
  - Waits 5 seconds for generation
  - Extracts 700x700 generated image
  - Filters out "loading" placeholder images

## Input Format

Campaign brief in `briefs/campaign.json`:

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
      "description": "Premium electrolyte water",
      "asset": "hydraboost.jpg"
    },
    {
      "name": "VitaSpark Energy",
      "description": "Natural vitamin energy drink",
      "asset": null
    }
  ]
}
```

Brand guidelines in `brands/{brand_id}/brand_guidelines.json`:

```json
{
  "brand_name": "HydraLife",
  "brand_id": "hydralife",
  "primary_color": "#0EA5E9",
  "secondary_color": "#38BDF8",
  "logo_path": "brands/hydralife/logo.png",
  "banned_words": ["cheap", "fake", "miracle"]
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
    │   ├── 1x1.png      # 1080x1080 Instagram Feed
    │   ├── 9x16.png     # 1080x1920 TikTok/Reels/Stories
    │   └── 16x9.png     # 1920x1080 YouTube/Facebook
    └── {Product_2}/
        ├── 1x1.png
        ├── 9x16.png
        └── 16x9.png
```

Example: `output/ecohome_Sustainable_Living_20260305_164155/`

Each pipeline run creates a single timestamped folder with brand_id prefix for easy brand identification.

## Lambda Services

### 1. Legal Check Service
**File**: `services/legal_check_service.py`
- Validates campaign message against banned words
- Ensures regulatory compliance

### 2. Asset Service
**File**: `services/asset_service.py`
- Checks if product assets exist
- Returns path or triggers generation

### 3. Image Generator Service
**File**: `services/image_generator_service.py`
- Supports two modes: Mock (default) and DeepAI (real generation)
- Mock mode: Uses random images from `input_assets/mock_generated/`
- DeepAI mode: Generates images via browser automation with Selenium
  - Uses `deepai_generator.py` for browser automation
  - Generates 700x700 images
  - Filters out loading placeholders
- Uses optimized prompts for advertising quality

### 4. Creative Scoring Service
**File**: `services/creative_scoring_service.py`
- Scores images with mock scores (random 7-9.5 range)
- In production: Can use GPT-4 Vision for real quality scoring
- Selects highest quality creative
- Evaluates: product visibility, ad quality, audience appeal

### 5. Image Processor Service
**File**: `services/image_processor_service.py`
- Creates aspect ratio variants
- Optimizes for social platforms

### 6. Creative Composer Service
**File**: `services/creative_composer_service.py`
- **Text Overlay**: 
  - Semi-transparent white background (70% opacity, RGB 255,255,255,179)
  - Background spans full image width, extends to bottom edge
  - Futura Bold 80px font (falls back to Futura, Montserrat, Impact, Helvetica)
  - Black text color, centered horizontally
  - 30px padding top, 60px total bottom padding
- **Logo Overlay**: Top-right corner placement
- Ensures brand consistency across all variants

### 7. Storage Service
**File**: `services/storage_service.py`
- Creates brand-organized output folders: `{brand_id}_{campaign_name}_{timestamp}`
- Organizes by product and aspect ratio
- Single timestamp per pipeline run for consistency

## Key Design Decisions

### 1. Multi-Candidate Generation + Scoring
Instead of generating one image, we:
- Generate multiple candidates
- Use vision model to score quality
- Select the best creative

**Why**: Dramatically improves output quality. Used by Meta, Google Ads, Canva.

### 2. Modular Lambda Architecture
Each pipeline step is an independent service.

**Why**: 
- Parallel execution
- Independent scaling
- Easy to replace/upgrade components

### 3. Brand Compliance Layer
Automatic enforcement of brand guidelines.

**Why**: 
- Ensures consistency across 100s of campaigns
- Reduces manual review
- Prevents regulatory issues

### 4. Asset Reuse Before Generation
Check storage before invoking GenAI.

**Why**: 
- Reduces GenAI costs
- Faster execution
- Consistent brand assets

### 5. Brand-Based Organization
Assets and guidelines organized by brand_id.

**Structure**:
```
input_assets/
├── {brand_id}/           # Brand-specific existing assets
└── mock_generated/       # Mock images for testing

brands/
└── {brand_id}/
    ├── brand_guidelines.json
    └── logo.png

output/
└── {brand_id}_{campaign}_{timestamp}/
```

**Why**:
- Multi-brand support out of the box
- Clear asset cataloging per brand
- Brand-specific compliance rules
- Scalable for enterprise with 100s of brands

## Scaling to Enterprise

### Current (POC)
```
Local Python Script
    ↓
Sequential Processing
    ↓
File System Storage
```

### Production Architecture
```
API Gateway
    ↓
Step Functions (Orchestrator)
    ↓
┌────────┬────────┬────────┬────────┐
Lambda   Lambda   Lambda   Lambda   (Parallel)
    ↓
S3 Storage
    ↓
CloudFront CDN
```

### Migration Path

| Component | POC | Production |
|-----------|-----|------------|
| **Orchestration** | main.py | API Gateway + Step Functions |
| **Compute** | Local functions | AWS Lambda |
| **Storage** | File system | S3 + CloudFront |
| **Triggers** | Manual | EventBridge (event-driven) |
| **Scaling** | Single process | Auto-scaling, parallel |
| **Monitoring** | Print statements | CloudWatch + X-Ray |

### Benefits at Scale

**100s of campaigns/month**:
- Parallel Lambda execution
- Event-driven triggers (new brief → auto-generate)
- Pay-per-use pricing

**Cost optimization**:
- Asset reuse reduces GenAI calls
- CLIP-based deduplication (future)
- Caching frequently used elements

**Quality control**:
- Vision-based scoring ensures quality
- Automated brand compliance
- A/B testing integration (future)

## Example Workflow

```bash
# 1. Create campaign brief
vim briefs/my_campaign.json

# 2. Add brand guidelines (if new brand)
mkdir -p brands/mybrand
vim brands/mybrand/brand_guidelines.json
cp logo.png brands/mybrand/

# 3. Add existing assets (optional)
mkdir -p input_assets/mybrand
cp product.jpg input_assets/mybrand/

# 4. Run pipeline (mock mode - fast testing)
python3 main.py briefs/my_campaign.json

# 5. Run with real image generation
python3 main.py briefs/my_campaign.json --deepai

# 6. Review outputs
open output/mybrand_My_Campaign_*/ProductName/1x1.png
```

## Advanced Features (Future)

### CLIP-Based Deduplication
```python
# Before generating, check similarity
embedding = get_clip_embedding(prompt)
similar = search_existing_assets(embedding)
if similarity > 0.9:
    reuse_asset(similar)
```

### Layout Rules Engine
```python
rules = {
    "logo_position": "top-right",
    "text_position": "lower-third",
    "min_product_size": "30%"
}
```

### Multi-Language Localization
```python
{
    "message": {
        "en": "Stay refreshed",
        "es": "Mantente fresco",
        "fr": "Restez rafraîchi"
    }
}
```

## Limitations & Future Improvements

- **Storage**: Local file system (production: S3 with CloudFront CDN)
- **Processing**: Sequential (production: parallel Lambda execution)
- **Scoring**: Mock random scores (production: GPT-4 Vision or Claude for real quality assessment)
- **Image Generation**: DeepAI browser automation (production: Bedrock with Stable Diffusion or Nova Canvas)
- **Typography**: Fixed text overlay design (future: dynamic layouts based on image content)
- **Validation**: Rule-based banned words (future: vision-based brand compliance checks)

## Dependencies

- **selenium**: Browser automation for DeepAI image generation
- **webdriver-manager**: Automatic ChromeDriver management
- **Pillow**: Image processing and text overlay rendering
- **requests**: HTTP requests for image downloads

**Font Requirements:**
- Futura Bold (preferred, system font on macOS)
- Fallbacks: Futura, Montserrat Bold, Impact, Helvetica

## Testing

```bash
# Test individual services
python -c "from services.legal_check_service import validate_message; validate_message('Test message', [])"

# Test full pipeline
python main.py
```

## Deployment to AWS

### Lambda Deployment
```bash
# Package each service
cd services
zip -r asset_service.zip asset_service.py ../utils/

# Upload to Lambda
aws lambda create-function \
  --function-name asset-service \
  --runtime python3.11 \
  --handler asset_service.lambda_handler \
  --zip-file fileb://asset_service.zip
```

### Step Functions Definition
```json
{
  "StartAt": "LegalCheck",
  "States": {
    "LegalCheck": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:legal-check",
      "Next": "AssetCheck"
    },
    "AssetCheck": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:asset-service",
      "Next": "GenerateOrReuse"
    }
  }
}
```

## Interview Talking Points

### System Design
- "Pipeline designed for serverless scaling with independent Lambda services"
- "API controller orchestrates workflow, easily replaced with Step Functions"

### Quality
- "Multi-candidate generation with vision-based scoring ensures high-quality output"
- "Similar to systems used by Meta Ads and Google Creative Studio"

### Cost Optimization
- "Asset reuse before generation reduces GenAI costs significantly"
- "Can add CLIP-based deduplication for further optimization"

### Brand Compliance
- "Automated brand enforcement ensures consistency across hundreds of campaigns"
- "Legal checks prevent regulatory issues before distribution"

### Scalability
- "Event-driven architecture supports 100s of campaigns monthly"
- "Parallel Lambda execution enables sub-minute generation times"

## License

MIT
