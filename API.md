# Creative Automation API

REST API design for the creative automation pipeline. Built for serverless deployment with AWS API Gateway + Lambda.

## Base URL
```
https://api.creative-automation.com/v1
```

## Authentication
```
Authorization: Bearer <jwt_token>
X-API-Key: <api_key>
```

## Core Endpoints

### 1. Generate Campaign
**POST** `/campaigns/generate`

Generate complete branded campaign assets.

**Request:**
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
    }
  ],
  "formats": ["1x1", "9x16", "16x9"],
  "generation_mode": "deepai"
}
```

**Response:**
```json
{
  "campaign_id": "camp_abc123",
  "status": "processing",
  "estimated_completion": "2024-01-15T10:30:00Z",
  "webhook_url": "https://your-app.com/webhooks/campaign-complete"
}
```

### 2. Get Campaign Status
**GET** `/campaigns/{campaign_id}`

**Response:**
```json
{
  "campaign_id": "camp_abc123",
  "status": "completed",
  "created_at": "2024-01-15T10:25:00Z",
  "completed_at": "2024-01-15T10:28:00Z",
  "brand_id": "hydralife",
  "campaign_name": "Summer Hydration",
  "assets": {
    "HydraBoost Water": {
      "1x1": "https://cdn.creative-automation.com/hydralife_Summer_Hydration_20240115/HydraBoost_Water/1x1.png",
      "9x16": "https://cdn.creative-automation.com/hydralife_Summer_Hydration_20240115/HydraBoost_Water/9x16.png",
      "16x9": "https://cdn.creative-automation.com/hydralife_Summer_Hydration_20240115/HydraBoost_Water/16x9.png"
    }
  },
  "quality_scores": {
    "HydraBoost Water": 8.7
  }
}
```

### 3. List Campaigns
**GET** `/campaigns`

Query parameters:
- `brand_id` (optional)
- `status` (optional): `processing`, `completed`, `failed`
- `limit` (default: 20)
- `offset` (default: 0)

**Response:**
```json
{
  "campaigns": [
    {
      "campaign_id": "camp_abc123",
      "campaign_name": "Summer Hydration",
      "brand_id": "hydralife",
      "status": "completed",
      "created_at": "2024-01-15T10:25:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

## Brand Management

### 4. Get Brand Guidelines
**GET** `/brands/{brand_id}`

**Response:**
```json
{
  "brand_id": "hydralife",
  "brand_name": "HydraLife",
  "primary_color": "#0EA5E9",
  "secondary_color": "#38BDF8",
  "logo_url": "https://cdn.creative-automation.com/brands/hydralife/logo.png",
  "banned_words": ["cheap", "fake", "miracle"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 5. Update Brand Guidelines
**PUT** `/brands/{brand_id}`

**Request:**
```json
{
  "brand_name": "HydraLife Premium",
  "primary_color": "#0EA5E9",
  "secondary_color": "#38BDF8",
  "banned_words": ["cheap", "fake", "miracle", "scam"]
}
```

### 6. Upload Brand Logo
**POST** `/brands/{brand_id}/logo`

**Request:** Multipart form data with image file

**Response:**
```json
{
  "logo_url": "https://cdn.creative-automation.com/brands/hydralife/logo.png",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

## Asset Management

### 7. Upload Product Asset
**POST** `/brands/{brand_id}/assets`

**Request:** Multipart form data
```
file: <image_file>
product_name: "HydraBoost Water"
```

**Response:**
```json
{
  "asset_id": "asset_xyz789",
  "product_name": "HydraBoost Water",
  "asset_url": "https://cdn.creative-automation.com/brands/hydralife/assets/hydraboost.jpg",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

### 8. List Brand Assets
**GET** `/brands/{brand_id}/assets`

**Response:**
```json
{
  "assets": [
    {
      "asset_id": "asset_xyz789",
      "product_name": "HydraBoost Water",
      "asset_url": "https://cdn.creative-automation.com/brands/hydralife/assets/hydraboost.jpg",
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

## Webhooks

### Campaign Completion
**POST** `{your_webhook_url}`

Sent when campaign generation completes.

**Payload:**
```json
{
  "event": "campaign.completed",
  "campaign_id": "camp_abc123",
  "status": "completed",
  "assets": {
    "HydraBoost Water": {
      "1x1": "https://cdn.creative-automation.com/...",
      "9x16": "https://cdn.creative-automation.com/...",
      "16x9": "https://cdn.creative-automation.com/..."
    }
  },
  "timestamp": "2024-01-15T10:28:00Z"
}
```

## Error Responses

All endpoints return consistent error format:

```json
{
  "error": {
    "code": "INVALID_BRAND_ID",
    "message": "Brand 'invalid_brand' not found",
    "details": {
      "available_brands": ["hydralife", "fitlife", "ecohome"]
    }
  },
  "request_id": "req_abc123"
}
```

**Common Error Codes:**
- `INVALID_BRAND_ID` (404)
- `CAMPAIGN_NOT_FOUND` (404)
- `GENERATION_FAILED` (500)
- `RATE_LIMIT_EXCEEDED` (429)
- `INVALID_REQUEST` (400)

## Rate Limits

- **Campaign Generation**: 10 requests/minute per API key
- **Asset Upload**: 50 requests/minute per API key
- **Read Operations**: 1000 requests/minute per API key

Headers included in responses:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642248000
```

## SDK Examples

### Python
```python
import requests

client = requests.Session()
client.headers.update({
    'Authorization': 'Bearer your_jwt_token',
    'X-API-Key': 'your_api_key'
})

# Generate campaign
response = client.post('https://api.creative-automation.com/v1/campaigns/generate', json={
    "campaign_name": "Summer Sale",
    "brand_id": "hydralife",
    "message": "Stay hydrated this summer",
    "products": [{"name": "Water Bottle", "description": "Premium water"}]
})

campaign = response.json()
print(f"Campaign ID: {campaign['campaign_id']}")
```

### JavaScript
```javascript
const client = axios.create({
  baseURL: 'https://api.creative-automation.com/v1',
  headers: {
    'Authorization': 'Bearer your_jwt_token',
    'X-API-Key': 'your_api_key'
  }
});

// Generate campaign
const response = await client.post('/campaigns/generate', {
  campaign_name: "Summer Sale",
  brand_id: "hydralife",
  message: "Stay hydrated this summer",
  products: [{name: "Water Bottle", description: "Premium water"}]
});

console.log(`Campaign ID: ${response.data.campaign_id}`);
```

## Architecture

```
Client Request
    ↓
API Gateway (Rate Limiting, Auth)
    ↓
Lambda Authorizer (JWT Validation)
    ↓
Campaign Lambda (Orchestrator)
    ↓
Step Functions (Pipeline Execution)
    ↓
┌─────────┬─────────┬─────────┬─────────┐
│ Legal   │ Asset   │Generator│ Scoring │ (Parallel Lambdas)
│ Check   │ Service │ Service │ Service │
└─────────┴─────────┴─────────┴─────────┘
    ↓
S3 Storage + CloudFront CDN
    ↓
Webhook Notification
```

## Deployment

**Infrastructure as Code (Terraform):**
```hcl
resource "aws_api_gateway_rest_api" "creative_automation" {
  name = "creative-automation-api"
}

resource "aws_lambda_function" "campaign_orchestrator" {
  function_name = "creative-automation-orchestrator"
  runtime      = "python3.9"
  handler      = "main.handler"
}
```

**Environment Variables:**
```bash
DEEPAI_API_KEY=your_deepai_key
S3_BUCKET=creative-automation-assets
CDN_DOMAIN=cdn.creative-automation.com
WEBHOOK_SECRET=your_webhook_secret
```