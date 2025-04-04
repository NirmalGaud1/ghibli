import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO
import textwrap
import numpy as np

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
    """Apply Ghibli color palette with proper mode handling"""
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert hex colors to RGB tuples
    palette = [tuple(int(c.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) 
              for c in GHIBLI_PALETTES[palette_name]]
    
    # Create palette image
    pal_image = Image.new("P", (16, 16))
    pal_image.putpalette(sum(palette, ()) * 51)  # Fill 256-color palette
    
    # Quantize and return as RGB
    return img.quantize(
        colors=len(palette),
        method=Image.Quantize.FASTOCTREE,
        palette=pal_image
    ).convert('RGB')

def cartoonize_image(img, palette_name):
    """Create strong cartoon effect with mode-safe operations"""
    # Ensure RGB mode
    img = img.convert('RGB')
    
    # 1. Enhance contrast and colors
    img = ImageEnhance.Contrast(img).enhance(1.8)
    img = ImageEnhance.Color(img).enhance(2.2)
    
    # 2. Create strong edges
    edges = img.filter(ImageFilter.FIND_EDGES)
    edges = edges.filter(ImageFilter.SMOOTH_MORE)
    edges = ImageOps.invert(edges.convert('L'))
    
    # 3. Apply Ghibli colors
    colored = apply_ghibli_colors(img, palette_name)
    
    # 4. Combine elements
    cartoon = Image.composite(colored, img, edges)
    
    # 5. Add painterly texture
    np_img = np.array(cartoon).astype(float)
    noise = np.random.normal(0, 25, np_img.shape)
    cartoon = Image.fromarray(np.uint8(np.clip(np_img + noise, 0, 255)))
    
    return cartoon.convert('RGBA')

def add_whimsical_text(img, text):
    """Add text overlay with proper mode handling"""
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Font loading with fallbacks
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
    st.title("🎨 Studio Ghibli Art Converter")
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    palette_choice = st.selectbox("Color Palette", list(GHIBLI_PALETTES.keys()))
    text_input = st.text_area("Caption", "Where magic comes alive...")
    
    if uploaded_file and st.button("Create Art"):
        with st.spinner("Painting your masterpiece..."):
            try:
                # Load and process image
                img = Image.open(uploaded_file)
                img = img.convert('RGB')  # Ensure initial RGB mode
                
                # Apply transformations
                cartoon = cartoonize_image(img, palette_choice)
                final_img = add_whimsical_text(cartoon, text_input)
                
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
