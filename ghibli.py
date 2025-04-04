import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

def generate_ghibli_style_image(image_bytes, text):
    """Generates a Ghibli-style image with overlaid text."""
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGBA")
        width, height = img.size
        font_size = int(height * 0.05)

        # Try multiple fonts in priority order
        try:
            font = ImageFont.truetype("arial.ttf", font_size)  # First choice
        except OSError:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)  # Fallback
            except OSError:
                font = ImageFont.load_default()  # Last resort
                st.warning("Custom fonts missing; using limited default font.")
                
        draw = ImageDraw.Draw(img)
        avg_char_width = font.getlength("A")
        if avg_char_width == 0:
            avg_char_width = 1  # Prevent division by zero
        textwrap_width = int(width / avg_char_width)
        wrapped_text = textwrap.fill(text, width=textwrap_width)

        # Calculate text dimensions using textbbox
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = (width - text_width) // 2
        text_y = height - text_height - int(height * 0.05)

        # Draw background rectangle
        draw.rectangle(
            (text_x - 10, text_y - 10, text_x + text_width + 10, text_y + text_height + 10),
            fill=(0, 0, 0, 128),
        )
        draw.text((text_x, text_y), wrapped_text, font=font, fill=(255, 255, 255, 255))

        return img

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

st.title("Ghibli Style Image Generator")

uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
text_input = st.text_area("Enter text to overlay", "A gentle breeze rustles the leaves.")

if uploaded_file is not None:
    image_bytes = uploaded_file.getvalue()

    if st.button("Generate Ghibli Image"):
        generated_image = generate_ghibli_style_image(image_bytes, text_input)

        if generated_image:
            st.image(generated_image, caption="Generated Ghibli Style Image")
            
            # Save image to bytes buffer for download
            img_buffer = BytesIO()
            generated_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            
            st.download_button(
                label="Download Image",
                data=img_buffer,
                file_name="ghibli_style_image.png",
                mime="image/png",
            )
else:
    st.info("Please upload an image to begin.")
