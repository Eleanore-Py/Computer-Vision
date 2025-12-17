import cv2
import mediapipe as mp
import numpy as np
import time
from scipy.spatial import distance as dist
import pandas as pd

# ===================== MEDIAPIPE SETUP =====================
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# ===================== PARAMETERS =====================
CONSEC_FRAMES = 3
CALIBRATION_TIME = 5      # seconds
BLINK_WINDOW = 60         # seconds (blink rate)
FATIGUE_BLINK_RATE = 25   # blinks/min
DROWSY_TIME = 1.5         # seconds

# ===================== VARIABLES =====================
COUNTER = 0
TOTAL_BLINKS = 0
blink_timestamps = []
ear_series = []
time_series = []

EAR_THRESHOLD = None
calibration_ears = []
eye_closed_time = 0

start_time = time.time()

# ===================== FUNCTIONS =====================
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

# ===================== CAMERA =====================
cap = cv2.VideoCapture(0)
print("[INFO] Eye Blink Detection Started...")
print("[INFO] Calibrating... Keep your eyes open")

# ===================== MAIN LOOP =====================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    current_time = time.time()
    elapsed_time = current_time - start_time

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = frame.shape
            left_eye, right_eye = [], []

            for idx in LEFT_EYE:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                left_eye.append((x, y))

            for idx in RIGHT_EYE:
                x = int(face_landmarks.landmark[idx].x * w)
                y = int(face_landmarks.landmark[idx].y * h)
                right_eye.append((x, y))

            ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

            # ===================== CALIBRATION =====================
            if EAR_THRESHOLD is None:
                calibration_ears.append(ear)
                cv2.putText(frame, "Calibrating...", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                if elapsed_time >= CALIBRATION_TIME:
                    mean_ear = np.mean(calibration_ears)
                    EAR_THRESHOLD = mean_ear * 0.75
                    print(f"[INFO] Calibration Done. EAR Threshold = {EAR_THRESHOLD:.2f}")
                continue

            # ===================== BLINK DETECTION =====================
            if ear < EAR_THRESHOLD:
                COUNTER += 1
                eye_closed_time += 1 / 30  # approx frame time
            else:
                if COUNTER >= CONSEC_FRAMES:
                    TOTAL_BLINKS += 1
                    blink_timestamps.append(current_time)
                COUNTER = 0
                eye_closed_time = 0

            # ===================== BLINK RATE =====================
            blink_rate = len([t for t in blink_timestamps if current_time - t <= BLINK_WINDOW])

            # ===================== FATIGUE DETECTION =====================
            fatigue_state = "Normal"
            if blink_rate > FATIGUE_BLINK_RATE:
                fatigue_state = "Fatigued"
            if eye_closed_time >= DROWSY_TIME:
                fatigue_state = "Drowsy"

            # ===================== LOG DATA =====================
            ear_series.append(ear)
            time_series.append(elapsed_time)

            # ===================== VISUALIZATION =====================
            cv2.polylines(frame, [np.array(left_eye)], True, (0, 255, 0), 1)
            cv2.polylines(frame, [np.array(right_eye)], True, (0, 255, 0), 1)

            cv2.putText(frame, f"Blinks: {TOTAL_BLINKS}", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

            cv2.putText(frame, f"Blink Rate: {blink_rate}/min", (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

            cv2.putText(frame, f"EAR: {ear:.2f}", (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

            cv2.putText(frame, f"State: {fatigue_state}", (20, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (0, 255, 0) if fatigue_state == "Normal" else (0, 0, 255), 2)

    cv2.imshow("Eye Blink & Fatigue Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ===================== SAVE EAR DATA =====================
df = pd.DataFrame({
    "time": time_series,
    "EAR": ear_series
})
df.to_csv("ear_timeseries.csv", index=False)
print("[INFO] EAR data saved to ear_timeseries.csv")

cap.release()
cv2.destroyAllWindows()
