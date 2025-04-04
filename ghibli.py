import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

# Studio Ghibli color palettes
GHIBLI_PALETTES = {
    "Mononoke": ["#3d2c2d", "#7a7770", "#c7c3b5", "#e3d8c2", "#d94e33"],
    "Totoro": ["#446a67", "#7a9f95", "#b7c9b1", "#e3e5d7", "#f7e7c3"],
    "Kiki": ["#4a5364", "#7b6a54", "#b89b72", "#e3d3a8", "#f4efd3"],
    "Spirited": ["#2d4350", "#556f7a", "#7f9da4", "#b7c9c5", "#e3e5d7"],
    "Laputa": ["#2d4b5e", "#5b7e8c", "#8fb1b3", "#c7d7c8", "#f0f0d1"],
    "Howl": ["#5e4d4a", "#927f7a", "#c7b8b1", "#e3d8c2", "#f7e7c3"],
    "Ponyo": ["#4a5364", "#7b6a54", "#b89b72", "#e3d3a8", "#f4efd3"],
    "Marnie": ["#3d2c2d", "#7a7770", "#c7c3b5", "#e3d8c2", "#d94e33"],
    "Princess": ["#2d4350", "#556f7a", "#7f9da4", "#b7c9c5", "#e3e5d7"]
}

def apply_ghibli_colors(img, palette_name):
    """Apply Ghibli color palette using optimized quantization"""
    img = img.convert('RGB')
    palette = [tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) 
              for c in GHIBLI_PALETTES[palette_name]]
    
    # Create palette image with 256 colors
    pal_image = Image.new("P", (16, 16))
    flattened = sum(palette, ())
    repeat = 256 // len(palette)
    remainder = 256 % len(palette)
    extended = (flattened * repeat) + flattened[:3*remainder]
    pal_image.putpalette(extended)
    
    return img.quantize(
        method=Image.Quantize.FASTOCTREE,
        palette=pal_image
    ).convert('RGB')

def cartoonify(img):
    """Create cartoon effect using OpenCV"""
    img_cv = np.array(img)
    img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    
    # Cartoonification pipeline
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img_cv, 9, 300, 300)
    cartoon_cv = cv2.bitwise_and(color, color, mask=edges)
    
    return Image.fromarray(cv2.cvtColor(cartoon_cv, cv2.COLOR_BGR2RGB))

def add_text_overlay(img, text):
    """Add stylized text overlay"""
    draw = ImageDraw.Draw(img.convert('RGBA'))
    width, height = img.size
    
    # Font handling
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
    
    if not font:
        font = ImageFont.load_default()
        st.warning("Install 'Luckiest Guy' font for best text results")
    
    # Text layout
    avg_char_width = font.getlength("A") or 1
    max_chars = int((width * 0.8) / avg_char_width)
    wrapped_text = textwrap.fill(text, width=max_chars)
    
    # Text positioning
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    text_y = height - (bbox[3] - bbox[1]) - int(height * 0.05)
    
    # Text effects
    for i in range(3):
        draw.text((text_x+i, text_y+i), wrapped_text, 
                 font=font, fill=(30, 30, 30, 200))
    draw.text((text_x, text_y), wrapped_text, 
             font=font, fill=(255, 245, 200, 240))
    
    return img

def main():
    st.title("🎨 Ghibli-Style Cartoonifier")
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    palette_choice = st.selectbox("Color Palette", list(GHIBLI_PALETTES.keys()))
    text_input = st.text_area("Caption", "Where magic comes alive...")
    
    if uploaded_file and st.button("Create Art"):
        with st.spinner("Creating magical artwork..."):
            try:
                # Load and process image
                img = Image.open(uploaded_file)
                cartoon = cartoonify(img)
                colored = apply_ghibli_colors(cartoon, palette_choice)
                final_img = add_text_overlay(colored, text_input)
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.image(img, caption="Original", use_container_width=True)
                with col2:
                    st.image(final_img, caption="Ghibli Style", use_container_width=True)
                
                # Download handling
                buf = BytesIO()
                final_img.save(buf, format="PNG")
                st.download_button(
                    "Download Artwork",
                    buf.getvalue(),
                    "ghibli_art.png",
                    "image/png"
                )
                
            except Exception as e:
                st.error(f"Error creating art: {str(e)}")

if __name__ == "__main__":
    main()
