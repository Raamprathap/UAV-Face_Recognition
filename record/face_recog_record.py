import cv2
import face_recognition
import os
import glob
import numpy as np
import time

class SmartFaceRecThreaded:
    def __init__(self, images_path="images", tracker_type="KCF", frame_resizing=0.25, process_every_n_frames=2, center_region_percent=0.6):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = frame_resizing
        self.process_every_n_frames = process_every_n_frames
        self.frame_count = 0
        self.fps = 0
        self.prev_time = time.time()
        self.center_region_percent = center_region_percent  # Focus on center X% of frame

        # Load face encodings
        self.load_encoding_images(images_path)

        # Load Haar Cascade for faster face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def load_encoding_images(self, images_path):
        images_path = glob.glob(os.path.join(images_path, "*.*"))
        if len(images_path) == 0:
            print(f"ERROR: No images found in '{images_path}'")
            exit()
        print(f"Found {len(images_path)} image(s). Loading...")
        for img_path in images_path:
            img = cv2.imread(img_path)
            if img is None:
                continue
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_img)
            if len(encodings) == 0:
                continue
            self.known_face_encodings.append(encodings[0])
            name = os.path.splitext(os.path.basename(img_path))[0]
            self.known_face_names.append(name)
        print(f"Encoding complete: {len(self.known_face_encodings)} faces loaded.")

    def detect_known_faces(self, frame):
        frame_height, frame_width = frame.shape[:2]
        
        # Calculate center region boundaries
        center_width = int(frame_width * self.center_region_percent)
        center_height = int(frame_height * self.center_region_percent)
        x_start = (frame_width - center_width) // 2
        y_start = (frame_height - center_height) // 2
        x_end = x_start + center_width
        y_end = y_start + center_height
        
        # Use Haar Cascade for initial fast detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_haar = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces_haar) == 0:
            return [], []
        
        # Filter faces to only include those in center region
        face_locations = []
        for (x, y, w, h) in faces_haar:
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            
            # Check if face center is within the center region
            if x_start <= face_center_x <= x_end and y_start <= face_center_y <= y_end:
                # Convert to (top, right, bottom, left) format
                face_locations.append((y, x+w, y+h, x))
        
        if len(face_locations) == 0:
            return [], []
        
        # Now do face recognition only on detected faces in center region
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            if len(self.known_face_encodings) > 0:
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_idx = np.argmin(distances)
                if matches[best_idx] and distances[best_idx] < 0.6:
                    name = self.known_face_names[best_idx]
            face_names.append(name)

        return face_locations, face_names

    def run(self, video_path=None, output_path=None):
        # Use video file if provided, otherwise use webcam
        if video_path:
            cap = cv2.VideoCapture(video_path)
            print(f"Opening video file: {video_path}")
        else:
            cap = cv2.VideoCapture(0)
            print("Opening webcam...")
        
        if not cap.isOpened():
            print("ERROR: Cannot open video source")
            exit()

        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Video FPS: {video_fps}, Total frames: {total_frames}, Size: {width}x{height}")

        # Setup video writer if output path is provided
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            writer = cv2.VideoWriter(output_path, fourcc, video_fps, (width, height))
            
            if writer.isOpened():
                print(f"Saving processed video to: {output_path}")
            else:
                print("ERROR: Could not open video writer")
                writer = None

        last_face_locations = []
        last_face_names = []
        start_time = time.time()
        
        # Calculate center region for visualization
        center_width = int(width * self.frame_resizing if hasattr(self, 'center_region_percent') else width * 0.6)
        center_height = int(height * self.frame_resizing if hasattr(self, 'center_region_percent') else height * 0.6)

        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Finished reading video")
                break

            self.frame_count += 1

            # Update FPS
            curr_time = time.time()
            self.fps = 1 / (curr_time - self.prev_time)
            self.prev_time = curr_time

            # Detect faces every N frames
            if self.frame_count % self.process_every_n_frames == 0:
                face_locations, face_names = self.detect_known_faces(frame)
                last_face_locations = face_locations
                last_face_names = face_names
            else:
                face_locations = last_face_locations
                face_names = last_face_names

            # Draw rectangles and names
            for (y1, x2, y2, x1), name in zip(face_locations, face_names):
                color = (0, 200, 0) if name != "Unknown" else (0, 0, 200)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                cv2.rectangle(frame, (x1, y1 - 30), (x2, y1), color, cv2.FILLED)
                cv2.putText(frame, name, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            # Draw center region rectangle (optional - for visualization)
            center_width = int(width * self.center_region_percent)
            center_height = int(height * self.center_region_percent)
            x_start = (width - center_width) // 2
            y_start = (height - center_height) // 2
            x_end = x_start + center_width
            y_end = y_start + center_height
            cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (255, 255, 0), 2)  # Yellow box showing detection zone

            # Display processing info
            cv2.putText(frame, f"Processing FPS: {int(self.fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
            if video_path:
                progress = (self.frame_count / total_frames) * 100
                elapsed = time.time() - start_time
                eta = (elapsed / self.frame_count) * (total_frames - self.frame_count)
                cv2.putText(frame, f"Frame: {self.frame_count}/{total_frames} ({progress:.1f}%) ETA: {int(eta)}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            
            # Write frame to output video if writer is available
            if writer:
                writer.write(frame)
            
            # Show frame
            cv2.imshow("Face Recognition", frame)

            key = cv2.waitKey(1)
            if key == 27:  # ESC
                print("Stopped by user")
                break

        if writer:
            writer.release()
            print(f"Video saved successfully to: {output_path}")
            # Get output file size
            if os.path.exists(output_path):
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"Output file size: {size_mb:.2f} MB")
        
        cap.release()
        cv2.destroyAllWindows()
        total_time = time.time() - start_time
        print(f"Processing complete! Total time: {int(total_time)}s ({total_time/60:.1f} minutes)")

if __name__ == "__main__":
    # CONFIGURATION - Update these paths before running
    video_file = "uploads/face_recognition.mp4"  # Path to input video file
    output_file = "output/processed_video.avi"   # Path to save processed video
    images_path = "images"                        # Folder containing known face images
    
    # Create output directory if it doesn't exist
    os.makedirs("output", exist_ok=True)
    
    # Initialize face recognition system
    # Parameters:
    # - frame_resizing: Scale factor for processing (0.5 = 50% size, faster but less accurate)
    # - process_every_n_frames: Process every Nth frame for speed (10 = process 1 in 10 frames)
    # - center_region_percent: Focus detection on center region (0.5 = center 50% of frame)
    sfr = SmartFaceRecThreaded(
        images_path=images_path,
        tracker_type="KCF", 
        frame_resizing=0.50,
        process_every_n_frames=10,
        center_region_percent=0.5
    )
    
    print("\nStarting video processing...")
    print(f"Input video: {video_file}")
    print(f"Output video: {output_file}")
    print(f"Known faces folder: {images_path}")
    print("-" * 60)
    
    sfr.run(video_path=video_file, output_path=output_file)
    