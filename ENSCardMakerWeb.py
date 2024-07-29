from flask import Flask, request, send_file
import requests
import json
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import textwrap
import io
import pydenticon
from io import BytesIO

app = Flask(__name__)

@app.route('/<user>', methods=['GET'])
def generate_card(user):
    if not user:
        return "Error: No user provided", 400
    
    profilerequest = requests.get(f"http://enstate.rs/u/{user}")
    if profilerequest.status_code != 200:
        return f"Error: Request failed with status code {profilerequest.status_code}", profilerequest.status_code
    
    profilejson = profilerequest.content.decode("utf-8")
    profile = json.loads(profilejson)
    
    avatar = None
    identicon_used = False
    fallback = False
    if 'avatar' in profile:
        try:
            avatar_response = requests.get(profile['avatar'], stream=True)
            avatar = Image.open(avatar_response.raw)

            if avatar.format == 'GIF':
                avatar = next(ImageSequence.Iterator(avatar))  # Get the first frame of the GIF

            avatar_size = (240, 240)  # Specify the desired size of the avatar image
            avatar = avatar.resize(avatar_size)  # Resize the avatar image

            # Ensure the image is in RGB mode
            if avatar.mode != 'RGB':
                avatar = avatar.convert('RGB')

            # Get the dominant color of the avatar
            dominant_color = avatar.getpixel((0, 0))

            # Darken the dominant color
            darkened_color = tuple(int(c * 0.5) for c in dominant_color)

            # Use the darkened color as the background color
            img = Image.new('RGB', (740, 290), color=darkened_color)

        except Exception as e:
            identicon_used = True
            fallback = True
            
            # Generate the identicon image
            identicon = pydenticon.Generator(5, 5).generate(profile['address'], 240, 240)

            # Convert the identicon image to PIL Image format
            avatar = Image.open(BytesIO(identicon))

            # Ensure the image is in RGB mode
            if avatar.mode != 'RGB':
                avatar = avatar.convert('RGB')

            # Get the dominant color of the avatar
            dominant_color = avatar.getpixel((0, 0))

            # Darken the dominant color
            darkened_color = tuple(int(c * 0.5) for c in dominant_color)

            # Use the darkened color as the background color
            img = Image.new('RGB', (740, 290), color=darkened_color)
    else:
        identicon_used = True
        
        # Generate the identicon image
        identicon = pydenticon.Generator(5, 5).generate(profile['address'], 240, 240)

        # Convert the identicon image to PIL Image format
        avatar = Image.fromarray(identicon)

        # Ensure the image is in RGB mode
        if avatar.mode != 'RGB':
            avatar = avatar.convert('RGB')

        # Get the dominant color of the avatar
        dominant_color = avatar.getpixel((0, 0))

        # Darken the dominant color
        darkened_color = tuple(int(c * 0.5) for c in dominant_color)

        # Use the darkened color as the background color
        img = Image.new('RGB', (740, 290), color=darkened_color)
        
    draw = ImageDraw.Draw(img)
    
    if avatar:
        avatar_size = (240, 240)  # Specify the desired size of the avatar image
        avatar = avatar.resize(avatar_size)  # Resize the avatar image
        img.paste(avatar, (20, 20))
        if profile['records']['avatar'].startswith("eip155:1/") and not identicon_used:
            # Draw a small box in the corner of the avatar
            box_position = (30, 30, 80, 60)  # Define the position of the box
            draw.rectangle(box_position, fill='#2081E2')
        
            # Draw the text "NFT" inside the box
            font_size = 20  # Specify the desired font size for the NFT text
            font_path = "./fonts/Inter-Bold.ttf"  # Path to the Inter Bold font
            font = ImageFont.truetype(font_path, font_size)  # Load the desired font
            draw.text((36, 33), "NFT", fill='white', font=font)  # Draw the text inside the box
        elif fallback:
            # Draw a small box in the corner of the avatar
            box_position = (30, 30, 150, 60)
            draw.rectangle(box_position, fill='#FF0000')
            
            # Draw the text "FALLBACK" inside the box
            font_size = 20
            font_path = "./fonts/Inter-Bold.ttf"
            font = ImageFont.truetype(font_path, font_size)
            draw.text((39, 33), "FALLBACK", fill='white', font=font)
        
    # Display the user's nickname, or replace it with their ENS name they don't have a nickname
    if 'name' in profile['records']:
        name = profile['records']['name']
        font_size = 48  # Specify the desired font size
        font_path = "./fonts/Inter-Bold.ttf"  # Path to the Inter Bold font
        font = ImageFont.truetype(font_path, font_size)  # Load the desired font
        draw.text((280, 20), name, fill=(255, 255, 255), font=font)  # Draw the text with the specified font
    elif 'name' in profile:
        name = profile['name']
        if '.' in name:
            name = name.split('.')[0]
        font_size = 48  # Specify the desired font size
        font_path = "./fonts/Inter-Bold.ttf"  # Path to the Inter Bold font
        font = ImageFont.truetype(font_path, font_size)  # Load the desired font
        draw.text((280, 20), name, fill=(255, 255, 255), font=font)  # Draw the text with the specified font
        
    # Display the user's ENS name and ETH address (truncated)
    if 'name' in profile and 'address' in profile:
        truncated_address = f"{profile['address'][:6]}...{profile['address'][-4:]}"
        idstring = f"{profile['name']} | {truncated_address}"
        font_size = 20  # Specify the desired font size
        font_path = "./fonts/Inter-Regular.ttf"  # Path to the Inter Regular font
        font = ImageFont.truetype(font_path, font_size)  # Load the desired font
        draw.text((280, 80), idstring, fill=(255, 255, 255), font=font)  # Draw the text with the specified font
        
    # Display the user's description with text wrapping
    description_y = 110
    if 'description' in profile['records']:
        description = profile['records']['description']
        font_size = 16  # Specify the desired font size
        font_path = "./fonts/Inter-Regular.ttf"  # Path to the Inter Regular font
        font = ImageFont.truetype(font_path, font_size)  # Load the desired font
        wrapped_description = textwrap.fill(description, width=50)
        wrapped_lines = wrapped_description.split('\n')
        if len(wrapped_lines) > 2:
            wrapped_lines = wrapped_lines[:2]
            wrapped_lines[-1] += '...'
        for line in wrapped_lines:
            draw.text((280, description_y), line, fill=(255, 255, 255), font=font)
            description_y += font_size + 4
    else:
        font_size = 16
        font_path = "./fonts/Inter-Regular.ttf"
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, description_y), f"[no description given]", fill=(255, 255, 255), font=font)
        description_y += font_size + 4
        
    # Social media
    social_media_spacing = 6
    social_media_y = description_y + 10
    if 'com.twitter' in profile['records']:
        twitter = profile['records']['com.twitter']
        font_size = 12  # Specify the desired font size
        font_path = "./fonts/Inter-Regular.ttf"  # Path to the Inter Regular font
        font = ImageFont.truetype(font_path, font_size)  # Load the desired font
        draw.text((280, social_media_y), f"Twitter: {twitter}", fill=(255, 255, 255), font=font)  # Draw the text with the specified font
    else:
        font_size = 12
        font_path = "./fonts/Inter-Regular.ttf"
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, social_media_y), f"[no Twitter given]", fill=(255, 255, 255), font=font)
        
    social_media_y += font_size + social_media_spacing
    if 'com.github' in profile['records']:
        github = profile['records']['com.github']
        font_size = 12  # Specify the desired font size
        font_path = "./fonts/Inter-Regular.ttf"  # Path to the Inter Regular font
        font = ImageFont.truetype(font_path, font_size)  # Load the desired font
        draw.text((280, social_media_y), f"GitHub: {github}", fill=(255, 255, 255), font=font)  # Draw the text with the specified font
    else:
        font_size = 12
        font_path = "./fonts/Inter-Regular.ttf"
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, social_media_y), f"[no GitHub given]", fill=(255, 255, 255), font=font)
        
    social_media_y += font_size + social_media_spacing
    if 'com.discord' in profile['records']:
        discord = profile['records']['com.discord']
        font_size = 12  # Specify the desired font size
        font_path = "./fonts/Inter-Regular.ttf"  # Path to the Inter Regular font
        font = ImageFont.truetype(font_path, font_size)  # Load the desired font
        draw.text((280, social_media_y), f"Discord: {discord}", fill=(255, 255, 255), font=font)  # Draw the text with the specified font
    else:
        font_size = 12
        font_path = "./fonts/Inter-Regular.ttf"
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, social_media_y), f"[no Discord given]", fill=(255, 255, 255), font=font)
        
    social_media_y += font_size + social_media_spacing
    if 'org.telegram' in profile['records']:
        telegram = profile['records']['org.telegram']
        font_size = 12  # Specify the desired font size
        font_path = "./fonts/Inter-Regular.ttf"  # Path to the Inter Regular font
        font = ImageFont.truetype(font_path, font_size)  # Load the desired font
        draw.text((280, social_media_y), f"Telegram: {telegram}", fill=(255, 255, 255), font=font)  # Draw the text with the specified font
    else:
        font_size = 12
        font_path = "./fonts/Inter-Regular.ttf"
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, social_media_y), f"[no Telegram given]", fill=(255, 255, 255), font=font)
        
    social_media_y += font_size + social_media_spacing
    if 'email' in profile['records']:
        email = profile['records']['email']
        font_size = 12  # Specify the desired font size
        font_path = "./fonts/Inter-Regular.ttf"  # Path to the Inter Regular font
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, social_media_y), f"Email: {email}", fill=(255, 255, 255), font=font)  # Draw the text with the specified font
    else:
        font_size = 12
        font_path = "./fonts/Inter-Regular.ttf"
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, social_media_y), f"[no email given]", fill=(255, 255, 255), font=font)
        
    social_media_y += font_size + social_media_spacing
    if 'url' in profile['records']:
        url = profile['records']['url']
        font_size = 12  # Specify the desired font size
        font_path = "./fonts/Inter-Regular.ttf"  # Path to the Inter Regular font
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, social_media_y), f"Website: {url}", fill=(255, 255, 255), font=font)  # Draw the text with the specified font
    else:
        font_size = 12
        font_path = "./fonts/Inter-Regular.ttf"
        font = ImageFont.truetype(font_path, font_size)
        draw.text((280, social_media_y), f"[no website given]", fill=(255, 255, 255), font=font)

    # Add watermark
    watermark_text = "enscards.littlebitstudios.com"
    watermark_font_size = 10
    watermark_font_path = "./fonts/Inter-Regular.ttf"
    watermark_font = ImageFont.truetype(watermark_font_path, watermark_font_size)
    watermark_bbox = draw.textbbox((0, 0), watermark_text, font=watermark_font)
    watermark_width = watermark_bbox[2] - watermark_bbox[0]
    watermark_height = watermark_bbox[3] - watermark_bbox[1]
    watermark_position = (img.width - watermark_width - 10, img.height - watermark_height - 10)

    # Define the RGBA color for the watermark text (e.g., slightly darker or transparent)
    watermark_color = (255, 255, 255, 128)  # White with 50% transparency

    # Create a new image for the watermark text with transparency
    watermark_image = Image.new('RGBA', img.size, (0, 0, 0, 0))
    watermark_draw = ImageDraw.Draw(watermark_image)
    watermark_draw.text(watermark_position, watermark_text, fill=watermark_color, font=watermark_font)

    # Composite the watermark image onto the original image
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, watermark_image)

    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
