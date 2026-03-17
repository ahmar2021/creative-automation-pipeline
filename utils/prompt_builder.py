REQUIRED_PRODUCT_FIELDS = ['name', 'description']
REQUIRED_BRIEF_FIELDS = ['audience', 'region']


def build_prompt(product, brief):
    for field in REQUIRED_PRODUCT_FIELDS:
        if field not in product:
            raise ValueError(f"Product missing required field: '{field}'")
    for field in REQUIRED_BRIEF_FIELDS:
        if field not in brief:
            raise ValueError(f"Brief missing required field: '{field}'")

    return f"""Create a vibrant social media advertisement image for the product with the following details. DO NOT include any text in the image other than the product name on the product itself.

Product: {product['name']}
Description: {product['description']}
Target Audience: {brief['audience']}
Region: {brief['region']}

Style: modern lifestyle advertising photography, clean and minimal
Lighting: professional commercial
Composition: product-focused with lifestyle context
"""
