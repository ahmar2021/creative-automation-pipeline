from PIL import Image, ImageDraw, ImageFont
import textwrap

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

FONT_PATHS = [
    ("/System/Library/Fonts/Supplemental/Futura.ttc", 1),
    ("/System/Library/Fonts/Supplemental/Futura.ttc", 0),
    ("/Users/ahmargh/Library/Fonts/Montserrat-Bold.ttf", None),
    ("/System/Library/Fonts/Supplemental/Impact.ttf", None),
    ("/System/Library/Fonts/Helvetica.ttc", None),
]

def _load_font(size):
    for path, index in FONT_PATHS:
        try:
            return ImageFont.truetype(path, size, index=index) if index is not None else ImageFont.truetype(path, size)
        except:
            continue
    return ImageFont.load_default()

def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines, current = [], []
    for word in words:
        test = ' '.join(current + [word])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return '\n'.join(lines)

def add_text_overlay(image_path, text, brand_color="#FFFFFF"):
    """Add text overlay with white background bar capped at 15% of image height."""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    max_bar_height = int(height * 0.15)
    padding = int(max_bar_height * 0.1)
    # Reserve ~40% of bar for CTA button
    cta_reserved = int(max_bar_height * 0.4)
    text_budget = max_bar_height - cta_reserved - padding * 2

    # Scale font to fit text within budget
    font_size = max(16, min(80, text_budget))
    while font_size >= 16:
        font_bold = _load_font(font_size)
        wrapped = _wrap_text(draw, text, font_bold, int(width * 0.85))
        bbox = draw.textbbox((0, 0), wrapped, font=font_bold)
        if bbox[3] - bbox[1] <= text_budget:
            break
        font_size -= 2

    text_height = bbox[3] - bbox[1]
    text_width = bbox[2] - bbox[0]

    # White bar: edge-to-edge, bottom-aligned, exactly max_bar_height tall
    bg_top = height - max_bar_height
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(overlay).rectangle(
        [(0, bg_top), (width, height)],
        fill=(255, 255, 255, 179)
    )
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Center text in the top portion of the bar
    x = (width - text_width) // 2
    y = bg_top + padding
    draw.text((x, y), wrapped, fill=(0, 0, 0), font=font_bold)

    img.save(image_path, quality=95)
    return image_path

def add_cta_button(image_path, brand_color="#0066FF", cta_text="Shop now"):
    """Add a CTA button in the lower portion of the 15% overlay bar."""
    img = Image.open(image_path).convert('RGBA')
    draw = ImageDraw.Draw(img)
    width, height = img.size

    max_bar_height = int(height * 0.15)
    cta_zone_height = int(max_bar_height * 0.4)
    cta_zone_top = height - cta_zone_height

    btn_font_size = max(16, cta_zone_height // 3)
    font = _load_font(btn_font_size)

    bbox = draw.textbbox((0, 0), cta_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    pad_x, pad_y = int(text_w * 0.4), int(text_h * 0.4)
    btn_w = text_w + pad_x * 2
    btn_h = text_h + pad_y * 2
    btn_x = (width - btn_w) // 2
    btn_y = cta_zone_top + (cta_zone_height - btn_h) // 2

    bg_color = hex_to_rgb(brand_color)
    draw.rounded_rectangle(
        [(btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h)],
        radius=btn_h // 2,
        fill=bg_color
    )

    tx = btn_x + (btn_w - text_w) // 2
    ty = btn_y + (btn_h - text_h) // 2
    draw.text((tx, ty), cta_text, fill=(255, 255, 255), font=font)

    img = img.convert('RGB')
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
