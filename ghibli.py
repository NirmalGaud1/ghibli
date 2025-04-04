import streamlit as st
import cv2
import numpy as np
import platform

def camera_test():
    """Test camera connectivity with different indexes"""
    st.subheader("🔍 Camera Troubleshooter")
    
    # Try different camera indexes
    for index in [0, 1, 2, 3]:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            st.success(f"✅ Found working camera at index {index}")
            ret, frame = cap.read()
            if ret:
                st.image(frame[:, :, ::-1], caption=f"Camera {index} Preview")
            cap.release()
            return index
        cap.release()
    
    st.error("❌ No cameras found. Possible reasons:")
    st.markdown("""
    1. Camera not connected
    2. Browser permissions not granted
    3. Another app is using the camera
    4. Virtual environment issues (Docker/WSL)
    """)
    return None

def cartoonify(frame):
    """Ghibli-style cartoon effect processing"""
    # Processing code from previous implementation
    # ...
    return processed_frame

def main():
    st.title("🎥 Ghibli Webcam Cartoonifier")
    
    st.markdown("""
    ### Troubleshooting Guide:
    1. **Refresh the page** and allow camera permissions
    2. **Close other apps** using the camera
    3. Try different **camera indexes** below
    4. On Linux: `sudo chmod 666 /dev/video*`
    """)
    
    # Camera selection
    selected_index = st.selectbox("Try camera indexes:", [0, 1, 2, 3])
    
    if st.button("Run Camera Test"):
        working_index = camera_test()
        if working_index is not None:
            st.session_state.working_index = working_index
    
    if "working_index" in st.session_state:
        st.write(f"🌟 Using camera index {st.session_state.working_index}")
        run = st.checkbox("Start Cartoonifier")
        
        if run:
            cap = cv2.VideoCapture(st.session_state.working_index)
            frame_window = st.image([])
            
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        st.error("Lost camera connection")
                        break
                    
                    processed = cartoonify(frame)
                    frame_window.image(processed[:, :, ::-1])
            
            finally:
                cap.release()
                cv2.destroyAllWindows()
    
    # Alternative video upload option
    st.subheader("...or upload a video file")
    uploaded_file = st.file_uploader("Choose video", type=["mp4", "avi", "mov"])
    # Add video processing logic here

if __name__ == "__main__":
    main()
