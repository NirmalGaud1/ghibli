import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import textwrap

def ghibli_cartoonify(image):
    """Create Ghibli-style painterly effect"""
    # Convert to OpenCV format
    img = np.array(image.convert('RGB')) 
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # 1. Create soft edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                cv2.THRESH_BINARY, 9, 9)
    
    # 2. Enhance colors Ghibli-style
    color = cv2.bilateralFilter(img, 9, 300, 300)
    color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    color = Image.fromarray(color)
    
    # 3. Add painterly texture
    color = color.filter(ImageFilter.SMOOTH_MORE)
    color = ImageEnhance.Color(color).enhance(1.4)
    color = ImageEnhance.Contrast(color).enhance(1.2)
    
    # 4. Combine with soft edges
    edges = Image.fromarray(edges).convert('L')
    edges = edges.filter(ImageFilter.GaussianBlur(1))
    cartoon = Image.composite(color, color, edges)
    
    # 5. Add signature Ghibli glow
    glow = cartoon.filter(ImageFilter.GaussianBlur(3))
    return Image.blend(cartoon, glow, 0.2)

def add_ghibli_text(img, text):
    """Add Ghibli-style text overlay"""
    draw = ImageDraw.Draw(img.convert('RGBA'))
    width, height = img.size
    
    # Font handling with fallbacks
    try:
        font_size = int(height * 0.06)
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Text wrapping
    avg_char_width = font.getlength("A") or 1
    max_chars = int((width * 0.8) / avg_char_width)
    wrapped_text = textwrap.fill(text, width=max_chars)
    
    # Text positioning
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_x = (width - (bbox[2]-bbox[0])) // 2
    text_y = height - (bbox[3]-bbox[1]) - int(height * 0.05)
    
    # Text effects
    draw.rectangle(
        (text_x-10, text_y-10, text_x + (bbox[2]-bbox[0])+10, text_y + (bbox[3]-bbox[1])+10),
        fill=(0, 0, 0, 128)
    )
    draw.text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255, 255))
    
    return img

def main():
    st.title("🍃 Ghibli-Style Cartoonifier")
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    text_input = st.text_area("Caption", "A world of wonder...")
    
    if uploaded_file and st.button("Create Magic"):
        with st.spinner("Painting your Studio Ghibli moment..."):
            try:
                # Load and process image
                original = Image.open(uploaded_file)
                cartoon = ghibli_cartoonify(original)
                final = add_ghibli_text(cartoon, text_input)
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.image(original, caption="Original", use_container_width=True)
                with col2:
                    st.image(final, caption="Ghibli Style", use_container_width=True)
                
                # Download
                buf = BytesIO()
                final.save(buf, format="PNG")
                st.download_button(
                    "📩 Download Artwork",
                    buf.getvalue(),
                    "ghibli_magic.png",
                    "image/png"
                )
                
            except Exception as e:
                st.error(f"Studio magic failed: {str(e)}")

if __name__ == "__main__":
    main()
