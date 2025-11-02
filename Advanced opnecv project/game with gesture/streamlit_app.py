import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

class IndexFingerSwipeTracker:
    def __init__(self):
        self.hands = mp_hands.Hands(min_detection_confidence=0.7, max_num_hands=1)
        self.last_pos = None
        self.swipe_threshold_x = 0.05
        self.swipe_threshold_y = 0.05
        self.cooldown = 0.5
        self.last_trigger = time.time()
        self.score = 0
        self.target_pos = self.generate_target()
        self.player_pos = [0.5, 0.5]  # Normalized coordinates

    def generate_target(self):
        return [np.random.random(), np.random.random()]

    def check_collision(self):
        # Check if player is close to target (using normalized coordinates)
        distance = np.sqrt(
            (self.player_pos[0] - self.target_pos[0])**2 + 
            (self.player_pos[1] - self.target_pos[1])**2
        )
        return distance < 0.1

    def detect_gesture(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        gesture = None
        hand_landmarks = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            index_tip = hand_landmarks.landmark[8]
            current_pos = (index_tip.x, index_tip.y)

            # Update player position based on index finger
            self.player_pos = [current_pos[0], current_pos[1]]

            if self.last_pos:
                dx = current_pos[0] - self.last_pos[0]
                dy = current_pos[1] - self.last_pos[1]

                if abs(dx) > self.swipe_threshold_x and abs(dx) > abs(dy):
                    gesture = "left" if dx > 0 else "right"
                elif abs(dy) > self.swipe_threshold_y and abs(dy) > abs(dx):
                    gesture = "down" if dy > 0 else "up"

            self.last_pos = current_pos

            # Check for collision with target
            if self.check_collision():
                self.score += 1
                self.target_pos = self.generate_target()
        else:
            self.last_pos = None

        return gesture, hand_landmarks, frame_rgb

def main():
    st.title("Hand Gesture Game 🎮")
    
    # Initialize game state
    if 'tracker' not in st.session_state:
        st.session_state.tracker = IndexFingerSwipeTracker()
        st.session_state.high_score = 0

    # Game layout
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("Game Stats")
        score_placeholder = st.empty()
        high_score_placeholder = st.empty()
        gesture_placeholder = st.empty()
        
        st.markdown("### How to Play")
        st.markdown("""
        - Move your index finger to control the player (blue dot)
        - Try to touch the target (red dot) to score points
        - Keep your hand visible in the camera
        - Wave your hand to move around
        """)

    with col1:
        st.subheader("Game View")
        frame_placeholder = st.empty()
        
        cap = cv2.VideoCapture(0)
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to access camera")
                    break

                # Flip frame horizontally for more intuitive interaction
                frame = cv2.flip(frame, 1)
                
                # Process frame
                gesture, landmarks, frame_rgb = st.session_state.tracker.detect_gesture(frame)
                
                # Draw hand landmarks
                if landmarks:
                    mp_drawing.draw_landmarks(
                        frame_rgb, landmarks, mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                    )

                # Draw player and target
                h, w = frame_rgb.shape[:2]
                # Draw target (red dot)
                target_x = int(st.session_state.tracker.target_pos[0] * w)
                target_y = int(st.session_state.tracker.target_pos[1] * h)
                cv2.circle(frame_rgb, (target_x, target_y), 15, (0, 0, 255), -1)
                
                # Draw player (blue dot)
                player_x = int(st.session_state.tracker.player_pos[0] * w)
                player_y = int(st.session_state.tracker.player_pos[1] * h)
                cv2.circle(frame_rgb, (player_x, player_y), 20, (255, 0, 0), -1)

                # Update display
                frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                
                # Update stats
                score = st.session_state.tracker.score
                if score > st.session_state.high_score:
                    st.session_state.high_score = score
                
                score_placeholder.metric("Score", score)
                high_score_placeholder.metric("High Score", st.session_state.high_score)
                if gesture:
                    gesture_placeholder.info(f"Last Gesture: {gesture.upper()}")

        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            cap.release()

if __name__ == "__main__":
    main()