import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def cartoonify(frame):
    """Real-time cartoon effect with proper color handling"""
    try:
        # Convert frame from BGR to RGB (webcam frames are BGR by default)
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
        
        # 4. Add Ghibli-style glow and convert back to BGR
        glow = cv2.GaussianBlur(cartoon, (21, 21), 0)
        cartoon = cv2.addWeighted(cartoon, 0.7, glow, 0.3, 0)
        return cv2.cvtColor(cartoon, cv2.COLOR_RGB2BGR)
    
    except Exception as e:
        st.error(f"Frame processing error: {str(e)}")
        return None

def main():
    st.title("🎥 Live Ghibli-Style Cartoonifier")
    
    run = st.checkbox("Start/Stop Webcam")
    FRAME_WINDOW = st.image([])
    camera = cv2.VideoCapture(0)

    while run:
        try:
            ret, frame = camera.read()
            if not ret:
                st.warning("Failed to capture frame")
                break
            
            # Process frame
            cartoon_frame = cartoonify(frame)
            
            if cartoon_frame is not None:
                # Convert BGR to RGB for proper display in Streamlit
                display_frame = cv2.cvtColor(cartoon_frame, cv2.COLOR_BGR2RGB)
                FRAME_WINDOW.image(display_frame)
        
        except Exception as e:
            st.error(f"Camera error: {str(e)}")
            break
    
    camera.release()
    cv2.destroyAllWindows()
    if not run:
        st.write("Webcam stopped")

if __name__ == "__main__":
    main()
