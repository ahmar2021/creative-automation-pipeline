def build_prompt(product, brief):
    return f"""Create a vibrant social media advertisement image.

Product: {product['name']}
Description: {product['description']}
Target Audience: {brief['audience']}
Region: {brief['region']}
Message: {product['name']}

Style: modern lifestyle advertising photography, clean and minimal
Lighting: professional commercial
Composition: product-focused with lifestyle context
"""
