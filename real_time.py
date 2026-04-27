"""
real_time.py  —  Production
Real-time human activity recognition using webcam + MediaPipe + HAR model.
Press Q to quit. Predictions saved to history.db every 3 seconds.

Run: python real_time.py

Requires: pip install opencv-python  (NOT opencv-python-headless)
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from collections import deque, Counter
import time

# ── Import shared components ──
from model_utils import load_har_model, DISPLAY_NAME, RISK_ACTIVITIES
from history_db import save_history

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
SEQ_LEN            = 60      # frames per prediction window
CONFIDENCE_THRESH  = 0.80    # raised — forces model to be very sure
SMOOTH_WINDOW      = 20      # larger window = more stable, less flicker
STEP_SIZE          = 5       # predict every N new frames
SAVE_INTERVAL_SEC  = 3.0     # save to DB at most once per N seconds
MIN_VOTE_RATIO     = 0.65    # at least 65% of buffer must agree
MODEL_PATH         = "models/activity_model.keras"
POSE_MODEL_PATH    = "pose_landmarker.task"

# Per-class thresholds — confused pairs need a higher bar
# Drinking is the most over-predicted class (most training samples)
# so it gets the highest threshold
PER_CLASS_THRESH = {
    "Drinking":    0.88,   # HIGHEST — most over-predicted
    "drinking":    0.88,
    "exercise":    0.85,   # confused with fighting
    "fighting":    0.85,   # confused with exercise
    "eating":      0.83,   # confused with drinking
    "Eating":      0.83,
    "no_activity": 0.75,   # can look like many things
    "no":          0.75,
}

# ─────────────────────────────────────────
# Load model & classes
# ─────────────────────────────────────────
print("Loading HAR model...")
model   = load_har_model(MODEL_PATH)
classes = np.load("classes.npy", allow_pickle=True)
print(f"Model loaded — {len(classes)} classes: {list(classes)}")

# ─────────────────────────────────────────
# MediaPipe setup
# ─────────────────────────────────────────
base_options = mp_python.BaseOptions(model_asset_path=POSE_MODEL_PATH)
options      = vision.PoseLandmarkerOptions(base_options=base_options)
landmarker   = vision.PoseLandmarker.create_from_options(options)


# ─────────────────────────────────────────
# Normalization 
# ─────────────────────────────────────────
def normalize_frame(frame: np.ndarray) -> np.ndarray:
    """Hip-center normalize a single (132,) frame."""
    out   = frame.copy()
    hip_l = frame[23*4:23*4+3]
    hip_r = frame[24*4:24*4+3]
    hip_c = (hip_l + hip_r) / 2.0
    sh_l  = frame[11*4:11*4+3]
    sh_r  = frame[12*4:12*4+3]
    scale = np.linalg.norm(sh_l - sh_r) + 1e-6
    for j in range(33):
        idx = j * 4
        out[idx:idx+3] = (frame[idx:idx+3] - hip_c) / scale
    return out


def extract_keypoints(result):
    """
    Return (132,) keypoints or None.
    Also checks visibility of critical landmarks (hips + shoulders).
    If hips are not visible, normalization is unreliable — skip the frame.
    """
    if not result.pose_landmarks:
        return None
    lms = result.pose_landmarks[0]
    # Check that BOTH hips (23,24) and BOTH shoulders (11,12) are visible
    # visibility < 0.5 means the landmark is likely off-screen or occluded
    critical = [11, 12, 23, 24]
    for idx in critical:
        if lms[idx].visibility < 0.5:
            return None  # Body too close / hips not in frame
    kp = []
    for lm in lms:
        kp.extend([lm.x, lm.y, lm.z, lm.visibility])
    return np.array(kp, dtype=np.float32)




def zscore_sequence(seq: np.ndarray) -> np.ndarray:
    """
    Z-score normalize (60, 132) sequence.
    MUST match create_dataset.py — this was the missing step
    causing wrong predictions at inference time.
    """
    mean = np.mean(seq)
    std  = np.std(seq)
    if std < 1e-6:
        return seq
    return (seq - mean) / (std + 1e-6)

# ─────────────────────────────────────────
# State
# ─────────────────────────────────────────
frame_buffer   = deque(maxlen=SEQ_LEN)
pose_valid     = False
pred_buffer    = deque(maxlen=SMOOTH_WINDOW)
frame_count    = 0
display_label  = "Warming up..."
display_conf   = 0.0
last_save_time = 0.0

# ─────────────────────────────────────────
# Open camera
# ─────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam. Check camera connection.")

print("Starting real-time detection. Press Q to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    h, w = frame.shape[:2]

    # ── Pose extraction ──
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_img)
    kp     = extract_keypoints(result)

    if kp is not None:
        frame_buffer.append(normalize_frame(kp))
        pose_valid = True
    else:
        pose_valid = False

    # ── Predict every STEP_SIZE frames when window is full ──
    if len(frame_buffer) == SEQ_LEN and frame_count % STEP_SIZE == 0:
        seq_raw = np.array(frame_buffer)         # (60, 132)
        seq_norm= zscore_sequence(seq_raw)            # z-score — MUST match create_dataset.py
        seq     = seq_norm[np.newaxis, ...]            # (1, 60, 132)
        probs   = model.predict(seq, verbose=0)[0]
        idx   = int(np.argmax(probs))
        conf  = float(probs[idx])
        pred_buffer.append((idx, conf))

        if len(pred_buffer) >= 3:
            idx_counts = Counter(p[0] for p in pred_buffer)
            best_idx, vote_count = idx_counts.most_common(1)[0]
            avg_conf    = float(np.mean([p[1] for p in pred_buffer if p[0] == best_idx]))
            raw_label   = classes[best_idx]

            # Use per-class threshold if defined, else global threshold
            threshold = PER_CLASS_THRESH.get(raw_label, CONFIDENCE_THRESH)

            # Also require majority: at least 60% of buffer agrees
            vote_ratio = vote_count / len(pred_buffer)

            if avg_conf >= threshold and vote_ratio >= MIN_VOTE_RATIO:
                display_label = DISPLAY_NAME.get(raw_label, raw_label)
                display_conf  = avg_conf
            else:
                display_label = "no_activity"
                display_conf  = avg_conf

            # Save to history DB
            now = time.time()
            if display_label not in ("...", "Warming up...") and (now - last_save_time) >= SAVE_INTERVAL_SEC:
                save_history(raw_label, display_conf)
                last_save_time = now

    # ── Draw overlay ──
    # Background bar
    cv2.rectangle(frame, (0, h-100), (w, h), (15, 18, 28), -1)

    # Pose validity warning
    if not pose_valid:
        cv2.putText(frame, "Move back & show full body (head to hip)",
                    (20, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 160, 255), 2, cv2.LINE_AA)

    # Activity label
    is_risk = any(r.lower() in display_label.lower() for r in RISK_ACTIVITIES)
    color   = (60, 80, 235) if is_risk else (0, 210, 100) if display_conf >= CONFIDENCE_THRESH else (100, 100, 110)
    label_text = f"Activity: {display_label}"
    cv2.putText(frame, label_text, (20, h-62),
                cv2.FONT_HERSHEY_SIMPLEX, 0.85, color, 2, cv2.LINE_AA)

    # Risk warning
    if is_risk:
        cv2.putText(frame, "RISK DETECTED", (20, h-30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (60, 80, 235), 2, cv2.LINE_AA)

    # Confidence bar
    bar_max = w - 40
    bar_w   = int(bar_max * min(display_conf, 1.0))
    cv2.rectangle(frame, (20, h-25), (20 + bar_max, h-10), (40, 45, 60), -1)
    cv2.rectangle(frame, (20, h-25), (20 + bar_w, h-10),   color, -1)
    cv2.putText(frame, f"{display_conf*100:.1f}%",
                (w - 70, h-12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 165, 180), 1, cv2.LINE_AA)

    # Landmark dots
    if result.pose_landmarks:
        for lm in result.pose_landmarks[0]:
            cx, cy = int(lm.x * w), int(lm.y * h)
            if 0 <= cx < w and 0 <= cy < h:
                cv2.circle(frame, (cx, cy), 3, (0, 200, 160), -1)

    cv2.imshow("HAR — Real Time Detection  (Q to quit)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print(model.summary())
print("Detection stopped.")
