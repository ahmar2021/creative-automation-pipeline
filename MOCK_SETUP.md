# Mock Setup Instructions

## To run the pipeline with mock images:

1. **Add your HydraBoost Water image:**
   - Place `hydraboost.jpg` in `input_assets/`

2. **Add mock generated images for VitaSpark Energy:**
   - Place one or more images in `input_assets/mock_generated/`
   - These will be used as mock outputs from the image generator
   - Supported formats: `.jpg`, `.png`

3. **Run the pipeline:**
   ```bash
   python3 main.py
   ```

## Current Setup:
- ✓ Image generator uses mock images (no OpenAI API calls)
- ✓ Scoring service uses mock scores (no OpenAI Vision API calls)
- ✓ All other services work normally

## Directory Structure:
```
input_assets/
├── hydraboost.jpg              # Existing asset for HydraBoost Water
├── logo.png                    # Brand logo (optional)
└── mock_generated/
    └── vitaspark_mock.jpg      # Mock generated image for VitaSpark
```
