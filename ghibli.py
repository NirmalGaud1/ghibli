import streamlit as st
import cv2
import numpy as np

def cartoonify(frame):
    """Ghibli-style cartoon effect"""
    try:
        # Convert to RGB for processing
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Edge detection
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        gray = cv2.medianBlur(gray, 5)
        edges = cv2.adaptiveThreshold(gray, 255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY, 9, 9)
        
        # Color processing
        color = cv2.bilateralFilter(img, 9, 300, 300)
        
        # Combine elements
        cartoon = cv2.bitwise_and(color, color, mask=edges)
        
        # Ghibli glow
        glow = cv2.GaussianBlur(cartoon, (21, 21), 0)
        return cv2.addWeighted(cartoon, 0.7, glow, 0.3, 0)
    
    except Exception as e:
        st.error(f"Processing error: {str(e)}")
        return None

def main():
    st.title("🎥 Ghibli Webcam Cartoonifier")
    
    # Camera selection
    cam_option = st.radio("Choose input:", ["Webcam", "Video File"])
    
    if cam_option == "Webcam":
        # Webcam setup with multiple camera attempts
        camera_idx = st.selectbox("Select camera index:", [0, 1, 2])
        
        try:
            camera = cv2.VideoCapture(camera_idx)
            if not camera.isOpened():
                st.error("Webcam not found. Try another index or upload a video.")
                return
        except Exception as e:
            st.error(f"Camera error: {str(e)}")
            return
        
        run = st.checkbox("Start Webcam")
        FRAME_WINDOW = st.image([])
        
        while run:
            ret, frame = camera.read()
            if not ret:
                st.warning("Failed to capture frame")
                break
            
            processed = cartoonify(frame)
            if processed is not None:
                FRAME_WINDOW.image(processed[:, :, ::-1])  # BGR to RGB conversion
        
        camera.release()
        st.write("Webcam session ended")

    else:  # Video File option
        uploaded_file = st.file_uploader("Upload video", type=["mp4", "avi", "mov"])
        if uploaded_file:
            # Save temporary video file
            with open("temp_vid", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process video
            cap = cv2.VideoCapture("temp_vid")
            FRAME_WINDOW = st.image([])
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                processed = cartoonify(frame)
                if processed is not None:
                    FRAME_WINDOW.image(processed[:, :, ::-1])
            
            cap.release()
            st.write("Video processing complete")

if __name__ == "__main__":
    main()
