from flask import Flask, render_template, Response
import cv2
import mediapipe as mp
import time
import json
from flask import jsonify

app = Flask(__name__)

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

    def detect_gesture(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        gesture = None
        hand_landmarks = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            index_tip = hand_landmarks.landmark[8]
            current_pos = (index_tip.x, index_tip.y)

            if self.last_pos:
                dx = current_pos[0] - self.last_pos[0]
                dy = current_pos[1] - self.last_pos[1]

                if abs(dx) > self.swipe_threshold_x and abs(dx) > abs(dy):
                    gesture = "left" if dx > 0 else "right"

                elif abs(dy) > self.swipe_threshold_y and abs(dy) > abs(dx):
                    gesture = "down" if dy > 0 else "up"

            self.last_pos = current_pos
        else:
            self.last_pos = None

        return gesture, hand_landmarks

tracker = IndexFingerSwipeTracker()
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gesture, landmarks = tracker.detect_gesture(frame)

            if landmarks:
                mp_drawing.draw_landmarks(
                    frame, landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=4),
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2)
                )

            if gesture:
                cv2.putText(frame, gesture.upper(), (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_gesture')
def get_gesture():
    success, frame = camera.read()
    if success:
        gesture, _ = tracker.detect_gesture(frame)
        return jsonify({'gesture': gesture if gesture else 'none'})
    return jsonify({'gesture': 'none'})

if __name__ == "__main__":
    app.run(debug=True)