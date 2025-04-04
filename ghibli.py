import streamlit as st
import cv2
import numpy as np
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont  # Correct imports

def cartoonify(image_path):
    """OpenCV-based cartoonifier with enhanced Ghibli-style effects"""
    # Read and convert image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 1. Create stronger edge mask
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 7)  # Increased from 5 to 7
    edges = cv2.adaptiveThreshold(gray, 255, 
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 11, 15)  # Increased block size and C value
    
    # 2. Enhanced color processing
    color = cv2.bilateralFilter(img, 12, 400, 400)  # Increased filter parameters
    
    # 3. Combine elements with stronger edges
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    # 4. More pronounced Ghibli-style glow
    glow = cv2.GaussianBlur(cartoon, (35, 35), 0)  # Increased kernel size
    cartoon = cv2.addWeighted(cartoon, 0.6, glow, 0.4, 0)  # Adjusted weights
    
    return cartoon

def add_ghibli_text(img_array, text):
    """Add stylized Ghibli text overlay"""
    pil_img = Image.fromarray(img_array)
    draw = ImageDraw.Draw(pil_img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Get text dimensions using modern method
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Position text at bottom center
    x = (pil_img.width - text_width) // 2
    y = pil_img.height - text_height - 20
    
    # Add background and text
    draw.rectangle(
        (x-10, y-10, x+text_width+10, y+text_height+10),
        fill=(0, 0, 0))
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    return np.array(pil_img)

def main():
    st.title("🎨 Studio Ghibli Cartoonifier")
    
    uploaded_file = st.file_uploader("Choose an image", 
                                   type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        # Save uploaded file temporarily
        with open("temp_img", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Process image
        cartoon = cartoonify("temp_img")
        final_image = add_ghibli_text(cartoon, "Studio Ghibli Magic")
        
        # Display results
        col1, col2 = st.columns(2)
        with col1:
            st.image(uploaded_file, caption="Original", 
                    use_container_width=True)
        with col2:
            st.image(final_image, caption="Ghibli Style", 
                    use_container_width=True)
        
        # Download functionality
        buf = BytesIO()
        Image.fromarray(final_image).save(buf, format="PNG")
        st.download_button(
            "✨ Download Artwork",
            buf.getvalue(),
            "ghibli_cartoon.png",
            "image/png"
        )
        
        # Cleanup temporary file
        os.remove("temp_img")

if __name__ == "__main__":
    main()
