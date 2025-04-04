import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def cartoonify(frame):
    """Real-time cartoon effect with Ghibli style"""
    # Convert to RGB
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 1. Create edge mask
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 9)
    
    # 2. Color enhancement
    color = cv2.bilateralFilter(img, 9, 300, 300)
    
    # 3. Combine edges and colors
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    # 4. Add Ghibli-style glow
    glow = cv2.GaussianBlur(cartoon, (21, 21), 0)
    cartoon = cv2.addWeighted(cartoon, 0.7, glow, 0.3, 0)
    
    return cartoon

def main():
    st.title("🎥 Live Ghibli-Style Cartoonifier")
    
    # Webcam controls
    run = st.checkbox("Start/Stop Webcam")
    FRAME_WINDOW = st.image([])
    camera = cv2.VideoCapture(0)

    while run:
        # Read frame from webcam
        _, frame = camera.read()
        
        # Process frame
        cartoon_frame = cartoonify(frame)
        
        # Convert to RGB for Streamlit
        cartoon_rgb = cv2.cvtColor(cartoon_frame, cv2.COLOR_BGR2RGB)
        
        # Display frame
        FRAME_WINDOW.image(cartoon_rgb)
    
    else:
        st.write("Webcam stopped")
        camera.release()

if __name__ == "__main__":
    main()
