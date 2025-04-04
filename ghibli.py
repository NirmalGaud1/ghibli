import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
from io import BytesIO
import textwrap
import numpy as np

def cartoonize_image(img):
    """Applies cartoon-like effects to the image"""
    # Convert to RGB for processing
    img = img.convert("RGB")
    
    # 1. Edge preservation and smoothing
    smoothed = img.filter(ImageFilter.SMOOTH_MORE)
    edges = smoothed.filter(ImageFilter.FIND_EDGES).convert("L")
    
    # 2. Enhanced color quantization (posterization)
    img = ImageOps.posterize(img, 4)
    
    # 3. Boost colors and contrast
    img = ImageEnhance.Color(img).enhance(1.6)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    
    # 4. Add painterly texture
    canvas_texture = Image.new("RGB", img.size, (255, 255, 255))
    noise = np.random.normal(0, 25, (img.size[1], img.size[0], 3))
    texture = Image.fromarray(np.uint8(np.clip(noise + 200, 0, 255)))
    img = Image.blend(img, texture, 0.1)
    
    # 5. Combine with edges for cartoon effect
    img = Image.composite(img, smoothed, edges)
    
    # 6. Add subtle vignette
    vignette = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(vignette)
    draw.ellipse((0, 0, img.width*1.5, img.height*1.5), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(100))
    img.putalpha(vignette)
    
    return img.convert("RGBA")

def add_whimsical_text(img, text):
    """Adds stylized text overlay"""
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Load cartoon-style font
    try:
        font_size = int(height * 0.06)
        font = ImageFont.truetype("LuckiestGuy-Regular.ttf", font_size)  # Free Google Font
    except:
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            st.warning("For best results, add 'LuckiestGuy-Regular.ttf' to your fonts")
    
    # Text wrapping and positioning
    avg_char_width = font.getlength("A")
    max_chars = int((width * 0.8) / avg_char_width) if avg_char_width > 0 else 30
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
    st.title("🎨 Ghibli-Style Cartoonifier")
    
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    text_input = st.text_area("Enter your magical caption", 
                            "Where spirits dance in the twilight...")
    
    if uploaded_file:
        if st.button("✨ Transform to Cartoon"):
            with st.spinner("Painting your masterpiece..."):
                try:
                    # Process image
                    original_img = Image.open(uploaded_file)
                    cartoon_img = cartoonize_image(original_img)
                    final_img = add_whimsical_text(cartoon_img, text_input)
                    
                    # Display comparison
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(original_img, caption="Original", use_column_width=True)
                    with col2:
                        st.image(final_img, caption="Ghibli Style", use_column_width=True)
                    
                    # Download functionality
                    buf = BytesIO()
                    final_img.save(buf, format="PNG", quality=90)
                    st.download_button(
                        label="📩 Download Artwork",
                        data=buf.getvalue(),
                        file_name="ghibli_cartoon.png",
                        mime="image/png"
                    )
                    
                except Exception as e:
                    st.error(f"Transformation failed: {str(e)}")

if __name__ == "__main__":
    main()
