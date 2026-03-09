# AWS Lambda Deployment Guide

## Overview

Each service in the `services/` directory is designed to be deployed as an independent AWS Lambda function. This guide shows how to deploy the pipeline to AWS.

## Architecture

```
API Gateway
    │
    ▼
Step Functions (Orchestrator)
    │
    ├─► Legal Check Lambda
    ├─► Asset Service Lambda
    ├─► Image Generator Lambda
    ├─► Scoring Service Lambda
    ├─► Image Processor Lambda
    ├─► Creative Composer Lambda
    └─► Storage Service Lambda
    │
    ▼
S3 Bucket (Output Storage)
```

## Prerequisites

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Install dependencies
pip install -r requirements.txt -t package/
```

## Step 1: Create Lambda Deployment Packages

### Legal Check Service

```bash
cd services
mkdir -p package
cp legal_check_service.py package/
cd package
zip -r ../legal_check_lambda.zip .
cd ..
```

### Asset Service

```bash
mkdir -p package
cp asset_service.py package/
cp -r ../utils package/
cd package
zip -r ../asset_service_lambda.zip .
cd ..
```

### Image Generator

```bash
mkdir -p package
pip install requests selenium webdriver-manager -t package/
cp image_generator_service.py deepai_generator.py package/
cd package
zip -r ../image_generator_lambda.zip .
cd ..
```

### Scoring Service

```bash
mkdir -p package
cp creative_scoring_service.py package/
cd package
zip -r ../scoring_service_lambda.zip .
cd ..
```

### Image Processor Service

```bash
mkdir -p package
pip install pillow -t package/
cp image_processor_service.py package/
cp -r ../utils package/
cd package
zip -r ../image_processor_lambda.zip .
cd ..
```

### Creative Composer Service

```bash
mkdir -p package
pip install pillow -t package/
cp creative_composer_service.py package/
cd package
zip -r ../composer_service_lambda.zip .
cd ..
```

## Step 2: Create Lambda Functions

### Create IAM Role

```bash
aws iam create-role \
  --role-name creative-automation-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy \
  --role-name creative-automation-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
  --role-name creative-automation-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Deploy Lambda Functions

```bash
# Legal Check
aws lambda create-function \
  --function-name creative-legal-check \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/creative-automation-lambda-role \
  --handler legal_check_service.lambda_handler \
  --zip-file fileb://legal_check_lambda.zip \
  --timeout 30 \
  --memory-size 256

# Asset Service
aws lambda create-function \
  --function-name creative-asset-service \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/creative-automation-lambda-role \
  --handler asset_service.lambda_handler \
  --zip-file fileb://asset_service_lambda.zip \
  --timeout 30 \
  --memory-size 256

# Image Generator
aws lambda create-function \
  --function-name creative-image-generator \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/creative-automation-lambda-role \
  --handler image_generator_service.lambda_handler \
  --zip-file fileb://image_generator_lambda.zip \
  --timeout 300 \
  --memory-size 1024 \
  --environment Variables={DEEPAI_API_KEY=your-key}

# Scoring Service
aws lambda create-function \
  --function-name creative-scoring-service \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/creative-automation-lambda-role \
  --handler creative_scoring_service.lambda_handler \
  --zip-file fileb://scoring_service_lambda.zip \
  --timeout 120 \
  --memory-size 512

# Image Processor
aws lambda create-function \
  --function-name creative-image-processor \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/creative-automation-lambda-role \
  --handler image_processor_service.lambda_handler \
  --zip-file fileb://image_processor_lambda.zip \
  --timeout 60 \
  --memory-size 512

# Creative Composer
aws lambda create-function \
  --function-name creative-composer-service \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/creative-automation-lambda-role \
  --handler creative_composer_service.lambda_handler \
  --zip-file fileb://composer_service_lambda.zip \
  --timeout 60 \
  --memory-size 512
```

## Step 3: Create S3 Bucket

```bash
aws s3 mb s3://creative-automation-assets
aws s3 mb s3://creative-automation-output
```

## Step 4: Create Step Functions State Machine

Create `state_machine.json`:

```json
{
  "Comment": "Creative Automation Pipeline",
  "StartAt": "LegalCheck",
  "States": {
    "LegalCheck": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:creative-legal-check",
      "Next": "AssetCheck"
    },
    "AssetCheck": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:creative-asset-service",
      "Next": "CheckAssetExists"
    },
    "CheckAssetExists": {
      "Type": "Choice",
      "Choices": [{
        "Variable": "$.body.asset_path",
        "IsNull": true,
        "Next": "GenerateImage"
      }],
      "Default": "ProcessImage"
    },
    "GenerateImage": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:creative-image-generator",
      "Next": "ScoreImages"
    },
    "ScoreImages": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:creative-scoring-service",
      "Next": "ProcessImage"
    },
    "ProcessImage": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:creative-image-processor",
      "Next": "ComposeCreatives"
    },
    "ComposeCreatives": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:REGION:ACCOUNT:function:creative-composer-service",
      "End": true
    }
  }
}
```

Deploy:

```bash
aws stepfunctions create-state-machine \
  --name creative-automation-pipeline \
  --definition file://state_machine.json \
  --role-arn arn:aws:iam::YOUR_ACCOUNT:role/step-functions-role
```

## Step 5: Create API Gateway

```bash
aws apigateway create-rest-api \
  --name creative-automation-api \
  --description "Creative Automation Pipeline API"

# Get API ID
API_ID=$(aws apigateway get-rest-apis --query "items[?name=='creative-automation-api'].id" --output text)

# Create resource
PARENT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[0].id' --output text)

aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $PARENT_ID \
  --path-part generate

# Create POST method
RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query "items[?path=='/generate'].id" --output text)

aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE
```

## Step 6: Test Deployment

```bash
# Invoke Step Functions
aws stepfunctions start-execution \
  --state-machine-arn arn:aws:states:REGION:ACCOUNT:stateMachine:creative-automation-pipeline \
  --input file://briefs/hydralife_campaign.json

# Check execution status
aws stepfunctions describe-execution \
  --execution-arn EXECUTION_ARN
```

## Cost Estimation

### Per Campaign (2 products, 3 formats each)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda (7 functions) | ~2 min total | $0.0001 |
| DeepAI | 2 products × 3 ratios | ~$0.06 |
| Scoring (mock) | 2 scores | $0.00 |
| S3 Storage | 6 images | $0.0001 |
| **Total** | | **~$0.10** |

### Monthly (100 campaigns)

- **Total**: ~$10/month
- **Scaling**: Linear with campaign count

## Monitoring

### CloudWatch Logs

```bash
aws logs tail /aws/lambda/creative-image-generator --follow
```

### X-Ray Tracing

Enable in Lambda console for distributed tracing.

### Metrics

- Lambda invocations
- Step Functions executions
- Error rates
- Duration

## Optimization Tips

1. **Use Lambda Layers** for shared dependencies (Pillow, OpenAI)
2. **Enable S3 Transfer Acceleration** for faster uploads
3. **Use CloudFront** for output distribution
4. **Implement SQS** for batch processing
5. **Add DynamoDB** for campaign metadata

## Rollback

```bash
# Delete Lambda functions
aws lambda delete-function --function-name creative-legal-check
aws lambda delete-function --function-name creative-asset-service
# ... repeat for all functions

# Delete Step Functions
aws stepfunctions delete-state-machine --state-machine-arn ARN

# Delete S3 buckets
aws s3 rb s3://creative-automation-assets --force
aws s3 rb s3://creative-automation-output --force
```

## Next Steps

1. Add EventBridge rules for automatic triggering
2. Implement DLQ for failed executions
3. Add SNS notifications for completion
4. Create CloudFormation template for IaC
5. Add CI/CD pipeline with GitHub Actions
