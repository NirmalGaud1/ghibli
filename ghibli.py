import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import textwrap

def generate_ghibli_style_image(image_bytes, text):
    """Generates a Ghibli-style image with overlaid text."""
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGBA")
        width, height = img.size

        try:
            font = ImageFont.truetype("arial.ttf", int(height * 0.05))
        except OSError:
            font = ImageFont.load_default()
            st.warning("Arial font not found, using default font.")

        draw = ImageDraw.Draw(img)
        wrapped_text = textwrap.fill(text, width=int(width / (font.getlength("A")) * 1.5))

        text_width, text_height = draw.textsize(wrapped_text, font=font)
        text_x = (width - text_width) / 2
        text_y = height - text_height - int(height * 0.05)

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
            st.download_button(
                label="Download Image",
                data=generated_image.tobytes(),
                file_name="ghibli_style_image.png",
                mime="image/png",
            )
else:
    st.info("Please upload an image to begin.")
