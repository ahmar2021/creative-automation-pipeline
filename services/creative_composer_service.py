from PIL import Image, ImageDraw, ImageFont
import textwrap

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def add_text_overlay(image_path, text, brand_color="#FFFFFF"):
    """Lambda-ready function to add text overlay with brand color"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    width, height = img.size
    color = hex_to_rgb(brand_color)
    
    # Use large fixed font size
    font_size = 80
    
    try:
        # Try Futura Bold
        font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Futura.ttc", font_size, index=1)
    except:
        try:
            # Fallback to regular Futura
            font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Futura.ttc", font_size)
        except:
            try:
                # Try Montserrat Bold (user fonts)
                font_bold = ImageFont.truetype("/Users/ahmargh/Library/Fonts/Montserrat-Bold.ttf", font_size)
            except:
                try:
                    # Fallback to Impact
                    font_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Impact.ttf", font_size)
                except:
                    try:
                        # Fallback to Helvetica
                        font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
                    except:
                        # Last resort: default font
                        font_bold = ImageFont.load_default()
    
    # Wrap text to fit 60% of width
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font_bold)
        test_width = bbox[2] - bbox[0]
        
        if test_width <= width * 0.6:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    wrapped_text = '\n'.join(lines)
    
    # Calculate text position
    bbox = draw.textbbox((0, 0), wrapped_text, font=font_bold)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Position text near bottom with padding
    x = (width - text_width) // 2
    text_padding_top = 30
    text_padding_bottom = 30
    y = height - text_height - text_padding_bottom
    
    # Draw semi-transparent white background bar (edge to edge, bottom to text top)
    bg_top = y - text_padding_top
    bg_bottom = height  # Extend to bottom edge
    
    # Create semi-transparent white background (70% opacity)
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [(0, bg_top), (width, bg_bottom)],
        fill=(255, 255, 255, 179)  # 179 = 70% opacity
    )
    
    # Composite overlay onto image
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, overlay)
    img = img.convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Draw text in dark color for contrast on white background
    text_color = (0, 0, 0)  # Black text on white background
    draw.text((x, y), wrapped_text, fill=text_color, font=font_bold)
    
    img.save(image_path, quality=95)
    return image_path

def add_logo(image_path, logo_path):
    """Lambda-ready function to add logo overlay"""
    if not logo_path or not os.path.exists(logo_path):
        return image_path
    
    base = Image.open(image_path)
    logo = Image.open(logo_path).convert("RGBA")
    
    # Resize logo proportionally
    logo_width = int(base.width * 0.15)
    aspect = logo.height / logo.width
    logo_height = int(logo_width * aspect)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
    
    # Position in top-right corner
    position = (base.width - logo_width - 30, 30)
    
    base.paste(logo, position, logo)
    base.save(image_path, quality=95)
    
    return image_path

import os

def lambda_handler(event, context):
    """AWS Lambda handler"""
    image_path = event.get("image_path")
    text = event.get("text")
    brand_color = event.get("brand_color", "#FFFFFF")
    logo_path = event.get("logo_path")
    
    add_text_overlay(image_path, text, brand_color)
    
    if logo_path:
        add_logo(image_path, logo_path)
    
    return {
        "statusCode": 200,
        "body": {"image_path": image_path}
    }
