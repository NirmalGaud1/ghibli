import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO
import textwrap
import numpy as np

def cartoonize_image(img):
    """Applies enhanced cartoon-like effects to the image"""
    # Convert to RGB for processing
    img = img.convert("RGB")
    
    # 1. Enhanced edge detection
    edges = img.filter(ImageFilter.FIND_EDGES).convert("L")
    edges = edges.filter(ImageFilter.SMOOTH_MORE).point(lambda x: 255 if x > 50 else 0)
    
    # 2. Color quantization and boosting
    img = ImageEnhance.Color(img).enhance(2.0)
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageOps.posterize(img, 3)
    
    # 3. Add painterly texture
    canvas = Image.new("RGB", img.size, (255, 255, 255))
    img = Image.blend(img, canvas, 0.1)
    
    # 4. Combine with edges
    cartoon = Image.composite(img, ImageOps.colorize(edges, "black", "white"), edges)
    
    # 5. Add warm vignette
    vignette = Image.new("L", cartoon.size, 0)
    draw = ImageDraw.Draw(vignette)
    draw.ellipse((-500, -500, cartoon.width+500, cartoon.height+500), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(800))
    cartoon.putalpha(vignette)
    
    return cartoon.convert("RGBA")

def add_whimsical_text(img, text):
    """Adds stylized text overlay with better font handling"""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Font handling with multiple fallbacks
    font_size = int(height * 0.06)
    font_paths = [
        "LuckiestGuy-Regular.ttf",
        "arial.ttf",
        "DejaVuSans-Bold.ttf"
    ]
    
    font = None
    for path in font_paths:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except OSError:
            continue
    
    if font is None:
        font = ImageFont.load_default()
        st.warning(
            "For best text results, download the 'Luckiest Guy' font from:\n"
            "https://fonts.google.com/specimen/Luckiest+Guy\n"
            "and place the .ttf file in your working directory."
        )
    
    # Text wrapping and positioning
    avg_char_width = font.getlength("A") if font.getlength("A") > 0 else 1
    max_chars = int((width * 0.8) / avg_char_width)
    wrapped_text = textwrap.fill(text, width=max_chars)
    
    # Text effects
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_x = (width - (bbox[2]-bbox[0])) // 2
    text_y = height - (bbox[3]-bbox[1]) - int(height * 0.05)
    
    # Text shadow effect
    for i in range(3):
        draw.text((text_x+i, text_y+i), wrapped_text, 
                 font=font, fill=(30, 30, 30, 200))
    
    # Main text
    draw.text((text_x, text_y), wrapped_text, 
             font=font, fill=(255, 245, 200, 240))
    
    return img

def main():
    st.title("🎨 Studio Ghibli-Style Cartoon Converter")
    
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    text_input = st.text_area("Enter your magical caption", 
                            "Where spirits dance in the twilight...")
    
    if uploaded_file:
        if st.button("✨ Transform to Ghibli Style"):
            with st.spinner("Creating magical artwork..."):
                try:
                    # Process image
                    original_img = Image.open(uploaded_file)
                    cartoon_img = cartoonize_image(original_img)
                    final_img = add_whimsical_text(cartoon_img, text_input)
                    
                    # Display comparison
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(original_img, caption="Original", use_container_width=True)
                    with col2:
                        st.image(final_img, caption="Ghibli Style", use_container_width=True)
                    
                    # Download functionality
                    buf = BytesIO()
                    final_img.save(buf, format="PNG", quality=90)
                    st.download_button(
                        label="📩 Download Artwork",
                        data=buf.getvalue(),
                        file_name="ghibli_magic.png",
                        mime="image/png"
                    )
                    
                except Exception as e:
                    st.error(f"Transformation failed: {str(e)}")

if __name__ == "__main__":
    main()
