import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from io import BytesIO
import textwrap
import numpy as np

def apply_ghibli_style(img):
    """Applies Studio Ghibli-inspired visual transformations"""
    # Convert to RGB for processing
    img = img.convert("RGB")
    
    # 1. Boost colors and contrast
    img = ImageEnhance.Color(img).enhance(1.3)  # More vibrant colors
    img = ImageEnhance.Contrast(img).enhance(1.2)  # Increased contrast
    
    # 2. Add painterly effect
    blurred = img.filter(ImageFilter.GaussianBlur(radius=2))
    edges = img.filter(ImageFilter.FIND_EDGES).convert("L")
    img = Image.composite(img, blurred, edges)
    
    # 3. Warm color temperature
    r, g, b = img.split()
    r = r.point(lambda i: i * 1.1)
    b = b.point(lambda i: i * 0.9)
    img = Image.merge("RGB", (r, g, b))
    
    # 4. Add subtle texture
    np_img = np.array(img).astype(float)
    noise = np.random.normal(0, 15, np_img.shape)
    np_img = np.clip(np_img + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(np_img)
    
    return img.convert("RGBA")

def add_text_overlay(img, text):
    """Adds styled text overlay to image"""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Font handling with fallbacks
    try:
        font_size = int(height * 0.045)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
            st.warning("Using default font - install Arial/DejaVu for better results")

    # Text wrapping calculation
    avg_char_width = sum(font.getlength(c) for c in "ABCDEFGHIJ")/10
    max_chars = int((width * 0.9) / avg_char_width) if avg_char_width > 0 else 35
    wrapped_text = textwrap.fill(text, width=max_chars)
    
    # Text positioning
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = height - text_height - int(height * 0.04)
    
    # Text background
    draw.rectangle(
        [x-10, y-10, x+text_width+10, y+text_height+10],
        fill=(0, 0, 0, 150)
    )
    
    # Text shadow
    draw.text((x+2, y+2), wrapped_text, font=font, fill=(0, 0, 0, 200))
    # Main text
    draw.text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 240))
    
    return img

def main():
    st.title("🎨 Ghibli Style Image Generator")
    
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    text_input = st.text_area("Enter caption", "A magical moment in the valley...")
    
    if uploaded_file:
        if st.button("✨ Create Ghibli Art"):
            with st.spinner("Working magic..."):
                try:
                    # Process image
                    img = Image.open(uploaded_file)
                    ghibli_img = apply_ghibli_style(img)
                    final_img = add_text_overlay(ghibli_img, text_input)
                    
                    # Display result
                    st.image(final_img, use_column_width=True)
                    
                    # Download button
                    buf = BytesIO()
                    final_img.save(buf, format="PNG")
                    st.download_button(
                        label="Download Artwork",
                        data=buf.getvalue(),
                        file_name="ghibli_art.png",
                        mime="image/png"
                    )
                    
                except Exception as e:
                    st.error(f"Magic failed: {str(e)}")

if __name__ == "__main__":
    main()
