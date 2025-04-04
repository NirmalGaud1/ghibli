import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import textwrap
import numpy as np
import matplotlib.colors as mcolors

# Studio Ghibli color palettes (curated from Movies in Color and ewenme/ghibli)
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
    """Applies Ghibli color palette using optimized quantization"""
    # Convert hex colors to RGB tuples
    palette = [tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) 
              for c in GHIBLI_PALETTES[palette_name]]
    
    # Create palette image
    pal_image = Image.new("P", (16, 16))
    pal_image.putpalette(sum(palette, ()))  # Flatten RGB tuples
    
    # Quantize image using selected palette
    return img.convert("RGB").quantize(
        colors=len(palette),
        method=Image.Quantize.FASTOCTREE,
        palette=pal_image
    ).convert("RGB")

def cartoonize_image(img, palette_name):
    """Creates Ghibli-style painterly effect"""
    # Edge detection and smoothing
    edges = img.filter(ImageFilter.FIND_EDGES).convert("L")
    smoothed = img.filter(ImageFilter.SMOOTH_MORE)
    
    # Apply Ghibli colors
    colored = apply_ghibli_colors(smoothed, palette_name)
    
    # Combine elements
    cartoon = Image.composite(colored, smoothed, edges)
    
    # Add signature Ghibli glow
    glow = cartoon.filter(ImageFilter.GaussianBlur(radius=3))
    return Image.blend(cartoon, glow, 0.3).convert("RGBA")

def add_whimsical_text(img, text):
    """Adds stylized text overlay with multiple font fallbacks"""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Font loading with priority order
    font_size = int(height * 0.06)
    font_paths = [
        "LuckiestGuy-Regular.ttf",  # Preferred font
        "arial.ttf",                # Windows/Mac default
        "DejaVuSans-Bold.ttf",      # Linux default
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
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
            "For best text results, download 'Luckiest Guy' from Google Fonts "
            "and place the .ttf file in your directory."
        )
    
    # Text layout calculations
    avg_char_width = font.getlength("A") if font.getlength("A") > 0 else 1
    max_chars = int((width * 0.8) / avg_char_width)
    wrapped_text = textwrap.fill(text, width=max_chars)
    
    # Text positioning
    bbox = draw.textbbox((0, 0), wrapped_text, font=font)
    text_x = (width - (bbox[2] - bbox[0])) // 2
    text_y = height - (bbox[3] - bbox[1]) - int(height * 0.05)
    
    # Text effects
    for i in range(3):  # Shadow layers
        draw.text((text_x+i, text_y+i), wrapped_text, 
                 font=font, fill=(30, 30, 30, 200))
    draw.text((text_x, text_y), wrapped_text,  # Main text
             font=font, fill=(255, 245, 200, 240))
    
    return img

def main():
    st.title("🎬 Studio Ghibli Art Converter")
    
    # UI Elements
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    palette_choice = st.selectbox("Film Color Palette", list(GHIBLI_PALETTES.keys()))
    text_input = st.text_area("Magical Caption", "Where spirits dance in the moonlight...")
    
    if uploaded_file and st.button("✨ Create Ghibli Art"):
        with st.spinner("Painting your story..."):
            try:
                # Process image
                original = Image.open(uploaded_file)
                ghibli_img = cartoonize_image(original, palette_choice)
                final_img = add_whimsical_text(ghibli_img, text_input)
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.image(original, caption="Original", use_container_width=True)
                with col2:
                    st.image(final_img, caption="Ghibli Style", use_container_width=True)
                
                # Download handling
                buf = BytesIO()
                final_img.save(buf, format="PNG", quality=90)
                st.download_button(
                    label="📥 Download Artwork",
                    data=buf.getvalue(),
                    file_name="ghibli_magic.png",
                    mime="image/png"
                )
                
            except Exception as e:
                st.error(f"Art creation failed: {str(e)}")

if __name__ == "__main__":
    main()
