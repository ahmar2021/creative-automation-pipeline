def build_prompt(product, brief):
    return f"""Create a vibrant social media advertisement image for the product with the following details. DO NOT include any text in the image other than the product name on the product itself.

Product: {product['name']}
Description: {product['description']}
Target Audience: {brief['audience']}
Region: {brief['region']}

Style: modern lifestyle advertising photography, clean and minimal
Lighting: professional commercial
Composition: product-focused with lifestyle context
"""
