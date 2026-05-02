"""
api.py — HAR AI Platform API
Accepts base64 video frames from browser, runs pose detection + model inference,
returns activity prediction. Saves to DB with username.

Run locally: uvicorn api:app --host 0.0.0.0 --port 8000
"""
import os
import io
import cv2
import base64
import numpy as np
from collections import deque, Counter
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from model_utils import load_har_model, DISPLAY_NAME, RISK_ACTIVITIES
from history_db  import save_history, get_history, init_history_db

# ── Init ──
app = FastAPI(title="HAR AI API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
init_history_db()

# ── Load model once at startup ──
print("Loading HAR model...")
MODEL   = load_har_model("models/activity_model.keras")
CLASSES = np.load("classes.npy", allow_pickle=True)
print(f"Model loaded — classes: {list(CLASSES)}")

# ── MediaPipe ──
base_options = mp_python.BaseOptions(model_asset_path="pose_landmarker.task")
options      = vision.PoseLandmarkerOptions(base_options=base_options)
LANDMARKER   = vision.PoseLandmarker.create_from_options(options)

# ── Config ──
SEQ_LEN           = 60
CONFIDENCE_THRESH = 0.80
SMOOTH_WINDOW     = 20
MIN_VOTE_RATIO    = 0.65

PER_CLASS_THRESH = {
    "Drinking": 0.90, "drinking": 0.90,
    "exercise": 0.85, "fighting": 0.85,
    "eating":   0.83, "Eating":   0.83,
    "no_activity": 0.70, "no": 0.70,
}

# ── Per-user state buffers ──
# Each user gets their own frame_buffer and pred_buffer
user_buffers: dict = {}

def get_user_buffer(username: str):
    if username not in user_buffers:
        user_buffers[username] = {
            "frames": deque(maxlen=SEQ_LEN),
            "preds":  deque(maxlen=SMOOTH_WINDOW),
            "last_save": 0.0,
            "last_label": "Warming up...",
            "last_conf": 0.0,
        }
    return user_buffers[username]


def normalize_frame(frame: np.ndarray) -> np.ndarray:
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


def zscore_sequence(seq: np.ndarray) -> np.ndarray:
    mean = np.mean(seq)
    std  = np.std(seq)
    if std < 1e-6:
        return seq
    return (seq - mean) / (std + 1e-6)


def extract_keypoints(result):
    if not result.pose_landmarks:
        return None
    lms      = result.pose_landmarks[0]
    critical = [11, 12, 23, 24]
    for idx in critical:
        if lms[idx].visibility < 0.5:
            return None
    kp = []
    for lm in lms:
        kp.extend([lm.x, lm.y, lm.z, lm.visibility])
    return np.array(kp, dtype=np.float32)


@app.post("/predict")
async def predict(request: Request):
    """
    Accepts: { "frame": "<base64 jpg>", "username": "mihir" }
    Returns: { "activity": "Eating", "confidence": 0.91, "pose_valid": true }
    """
    try:
        data     = await request.json()
        username = data.get("username", "unknown")
        frame_b64= data.get("frame", "")

        if not frame_b64:
            return JSONResponse({"activity": None, "confidence": 0, "pose_valid": False})

        # Decode base64 frame
        img_bytes = base64.b64decode(frame_b64.split(",")[-1])
        img_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img_bgr   = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if img_bgr is None:
            return JSONResponse({"activity": None, "confidence": 0, "pose_valid": False})

        # MediaPipe pose detection
        rgb    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = LANDMARKER.detect(mp_img)
        kp     = extract_keypoints(result)

        buf = get_user_buffer(username)

        if kp is None:
            # Body not fully in frame — clear buffers
            buf["frames"].clear()
            buf["preds"].clear()
            buf["last_label"] = "Show full body..."
            buf["last_conf"]  = 0.0
            return JSONResponse({
                "activity":   None,
                "label":      "Show full body...",
                "confidence": 0.0,
                "pose_valid": False,
            })

        buf["frames"].append(normalize_frame(kp))

        # Predict when buffer is full
        if len(buf["frames"]) == SEQ_LEN:
            seq_raw  = np.array(buf["frames"])
            seq_norm = zscore_sequence(seq_raw)
            seq      = seq_norm[np.newaxis, ...]
            probs    = MODEL.predict(seq, verbose=0)[0]
            idx      = int(np.argmax(probs))
            conf     = float(probs[idx])
            buf["preds"].append((idx, conf))

            if len(buf["preds"]) >= 3:
                idx_counts           = Counter(p[0] for p in buf["preds"])
                best_idx, vote_count = idx_counts.most_common(1)[0]
                avg_conf             = float(np.mean([p[1] for p in buf["preds"] if p[0] == best_idx]))
                raw_label            = CLASSES[best_idx]
                threshold            = PER_CLASS_THRESH.get(raw_label, CONFIDENCE_THRESH)
                vote_ratio           = vote_count / len(buf["preds"])

                if avg_conf >= threshold and vote_ratio >= MIN_VOTE_RATIO:
                    display = DISPLAY_NAME.get(raw_label, raw_label)
                    buf["last_label"] = display
                    buf["last_conf"]  = avg_conf

                    # Save to DB every 3 seconds
                    import time
                    now = time.time()
                    if now - buf["last_save"] >= 3.0:
                        save_history(raw_label, avg_conf, username=username)
                        buf["last_save"] = now
                else:
                    buf["last_label"] = "..."
                    buf["last_conf"]  = avg_conf

        return JSONResponse({
            "activity":   buf["last_label"],
            "confidence": buf["last_conf"],
            "pose_valid": True,
            "is_risk":    buf["last_label"] in RISK_ACTIVITIES,
        })

    except Exception as e:
        return JSONResponse({"error": str(e), "activity": None, "confidence": 0}, status_code=500)


@app.get("/latest_activity")
async def latest_activity(username: str = "unknown"):
    """Poll latest activity for a user — called by browser every 2s."""
    buf = get_user_buffer(username)
    raw = get_history(username=username)
    total = len(raw)
    return JSONResponse({
        "activity":      buf["last_label"],
        "confidence":    buf["last_conf"],
        "total_records": total,
    })


@app.get("/health")
async def health():
    return {"status": "ok", "model": "loaded", "classes": list(CLASSES)}