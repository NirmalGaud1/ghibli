import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import textwrap

def ghibli_cartoonify(image):
    """Create Studio Ghibli-style painterly effect"""
    # Convert to OpenCV format
    img = np.array(image.convert('RGB')) 
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # 1. Edge detection with soft blur
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY, 9, 9)
    
    # 2. Color enhancement
    color = cv2.bilateralFilter(img, 9, 300, 300)
    color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    color = Image.fromarray(color)
    
    # 3. Ghibli-style enhancements
    color = color.filter(ImageFilter.SMOOTH_MORE)
    color = ImageEnhance.Color(color).enhance(1.4)  # Boost colors
    color = ImageEnhance.Contrast(color).enhance(1.2)  # Increase contrast
    
    # 4. Combine elements with soft edges
    edges = Image.fromarray(edges).convert('L')
    edges = edges.filter(ImageFilter.GaussianBlur(1))
    cartoon = Image.composite(color, color, edges)
    
    # 5. Add signature Ghibli glow
    glow = cartoon.filter(ImageFilter.GaussianBlur(3))
    return Image.blend(cartoon, glow, 0.2)

def add_ghibli_text(img, text):
    """Add Studio Ghibli-style text overlay"""
    draw = ImageDraw.Draw(img.convert('RGBA'))
    width, height = img.size
    
    # Font handling with fallbacks
    font_size = int(height * 0.06)
    font = None
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Text wrapping and positioning
    avg_char_width = font.getlength("A") if font.getlength("A") > 0 else 1
    max_chars = int((width * 0.8) / avg_char_width)
    wrapped_text = textwrap.fill(text, width=int(max_chars))
    
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    text_y = height - (bbox[3] - bbox[1]) - int(height * 0.05)
    
    # Text background and styling
    draw.rectangle(
        (text_x-10, text_y-10, text_x + (bbox[2]-bbox[0])+10, text_y + (bbox[3]-bbox[1])+10),
        fill=(0, 0, 0, 128))
    draw.text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255, 255))
    
    return img

def main():
    st.title("🍃 Studio Ghibli Magic Maker")
    
    uploaded_file = st.file_uploader("Upload Your Image", type=["jpg", "jpeg", "png"])
    text_input = st.text_area("Add Your Magical Caption", "Where spirits dance...")
    
    if uploaded_file and st.button("Create Ghibli Art"):
        with st.spinner("Painting your Studio Ghibli moment..."):
            try:
                # Process image
                original = Image.open(uploaded_file)
                cartoon = ghibli_cartoonify(original)
                final_image = add_ghibli_text(cartoon, text_input)
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.image(original, caption="Original", use_container_width=True)
                with col2:
                    st.image(final_image, caption="Ghibli Style", use_container_width=True)
                
                # Download handling
                buf = BytesIO()
                final_image.save(buf, format="PNG")
                st.download_button(
                    "✨ Download Your Artwork",
                    buf.getvalue(),
                    "ghibli_magic.png",
                    "image/png"
                )
                
            except Exception as e:
                st.error(f"Magic failed: {str(e)}")

if __name__ == "__main__":
    main()
