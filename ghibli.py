import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from io import BytesIO

def cartoonify(image_path):
    # Read image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 1. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # 2. Apply median blur
    gray = cv2.medianBlur(gray, 5)
    
    # 3. Detect edges
    edges = cv2.adaptiveThreshold(gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 9)
    
    # 4. Apply bilateral filter
    color = cv2.bilateralFilter(img, 9, 300, 300)
    
    # 5. Combine edges and color image
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    # Add Ghibli-style glow
    glow = cv2.GaussianBlur(cartoon, (21, 21), 0)
    cartoon = cv2.addWeighted(cartoon, 0.7, glow, 0.3, 0)
    
    return cartoon

def add_ghibli_text(img, text):
    pil_img = Image.fromarray(img)
    draw = ImageDraw.Draw(pil_img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text_width, text_height = draw.textsize(text, font)
    x = (pil_img.width - text_width) // 2
    y = pil_img.height - text_height - 20
    
    # Text background
    draw.rectangle((x-10, y-10, x+text_width+10, y+text_height+10), fill=(0,0,0))
    draw.text((x, y), text, font=font, fill=(255,255,255))
    
    return np.array(pil_img)

def main():
    st.title("🎨 Ghibli-Style Cartoonifier")
    
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Save uploaded file
        with open("temp_image", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Process image
        cartoon_image = cartoonify("temp_image")
        final_image = add_ghibli_text(cartoon_image, "Studio Ghibli Magic")
        
        # Display results
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, caption="Original Image", use_column_width=True)
        with col2:
            st.image(final_image, caption="Cartoon Version", use_column_width=True)
        
        # Download button
        buf = BytesIO()
        Image.fromarray(final_image).save(buf, format="PNG")
        st.download_button(
            label="Download Cartoon Image",
            data=buf.getvalue(),
            file_name="ghibli_cartoon.png",
            mime="image/png"
        )
        
        # Cleanup
        os.remove("temp_image")

if __name__ == "__main__":
    main()
