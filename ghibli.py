import streamlit as st
import cv2
import numpy as np

def cartoonify(frame):
    """Real-time Ghibli-style cartoon effect"""
    # Convert to RGB
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # 1. Edge detection
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, 9, 9)
    
    # 2. Color processing
    color = cv2.bilateralFilter(img, 9, 300, 300)
    
    # 3. Combine elements
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    
    # 4. Ghibli glow effect
    glow = cv2.GaussianBlur(cartoon, (21, 21), 0)
    return cv2.addWeighted(cartoon, 0.7, glow, 0.3, 0)

def main():
    st.title("🎥 Live Ghibli Cartoonifier")
    
    run = st.checkbox("Start Webcam")
    FRAME_WINDOW = st.image([])
    
    # Initialize camera with error handling
    try:
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            st.error("Could not access webcam")
            return
    except Exception as e:
        st.error(f"Camera initialization failed: {str(e)}")
        return

    while run:
        try:
            ret, frame = camera.read()
            if not ret:
                st.warning("Failed to capture frame")
                break
            
            # Process and display frame
            processed = cartoonify(frame)
            FRAME_WINDOW.image(processed[:, :, ::-1])  # Convert BGR to RGB
            
        except Exception as e:
            st.error(f"Processing error: {str(e)}")
            break

    # Cleanup resources
    camera.release()
    st.write("Webcam session ended")

if __name__ == "__main__":
    main()
