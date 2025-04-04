import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO
import textwrap
import numpy as np
import matplotlib.colors as mcolors

GHIBLI_PALETTES = {
    "Mononoke": ["#3d2c2d", "#7a7770", "#c7c3b5", "#e3d8c2", "#d94e33"],
    "Totoro": ["#446a67", "#7a9f95", "#b7c9b1", "#e3e5d7", "#f7e7c3"],
    # ... (keep other palettes the same)
}

def apply_ghibli_colors(img, palette_name):
    """Enhanced color quantization with dithering"""
    palette = [tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) 
              for c in GHIBLI_PALETTES[palette_name]]
    
    # Create optimized palette image
    pal_image = Image.new("P", (16, 16))
    pal_image.putpalette(sum(palette, ()) * 3)  # Extend for 256 colors
    
    return img.convert("RGB").quantize(
        colors=len(palette),
        method=Image.Quantize.FASTOCTREE,
        dither=Image.Dither.FLOYDSTEINBERG,
        palette=pal_image
    ).convert("RGB")

def cartoonize_image(img, palette_name):
    """Stronger cartoon effect with multiple processing steps"""
    # 1. Enhance base image
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Color(img).enhance(2.0)
    
    # 2. Create pronounced edges
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges = edges.filter(ImageFilter.MaxFilter(3))
    edges = ImageOps.invert(edges).convert("L")
    
    # 3. Apply palette colors
    colored = apply_ghibli_colors(img, palette_name)
    
    # 4. Combine elements with multiple layers
    base = Image.composite(colored, img, edges)
    
    # 5. Add painterly texture
    texture = Image.effect_mandelbrot(
        img.size, 
        (-3, -2.5, 2, 2.5), 
        100
    ).convert("L").resize(img.size)
    final = Image.blend(base, ImageOps.colorize(texture, "#000000", "#ffffff"), 0.1)
    
    # 6. Final enhancements
    final = final.filter(ImageFilter.SMOOTH_MORE)
    return ImageEnhance.Sharpness(final).enhance(2.0).convert("RGBA")

def add_whimsical_text(img, text):
    # ... (keep previous text implementation) ...

def main():
    st.title("🎨 Studio Ghibli Style Converter")
    
    uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
    palette_choice = st.selectbox("Choose Palette", list(GHIBLI_PALETTES.keys()))
    intensity = st.slider("Artistic Intensity", 1.0, 3.0, 2.0)
    
    if uploaded_file and st.button("Create Art"):
        with st.spinner("Painting your masterpiece..."):
            try:
                img = Image.open(uploaded_file)
                
                # Apply transformations
                img = img.resize((1024, int(1024 * img.height/img.width)))  # Standardize size
                cartoon = cartoonize_image(img, palette_choice)
                final = add_whimsical_text(cartoon, "Ghibli Magic!")
                
                # Display comparison
                col1, col2 = st.columns(2)
                with col1: st.image(img, caption="Original", use_container_width=True)
                with col2: st.image(final, caption="Ghibli Style", use_container_width=True)
                
                # Download
                buf = BytesIO()
                final.save(buf, format="PNG")
                st.download_button("Download Art", buf.getvalue(), "ghibli_art.png", "image/png")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
