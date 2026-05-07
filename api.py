# """
# api.py — HAR AI Platform API
# Accepts base64 video frames from browser, runs pose detection + model inference,
# returns activity prediction. Saves to DB with username.

# Run locally: uvicorn api:app --host 0.0.0.0 --port 8000
# """
# import os
# import io
# import cv2
# import base64
# import numpy as np
# from collections import deque, Counter
# from datetime import datetime
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# import mediapipe as mp
# from mediapipe.tasks import python as mp_python
# from mediapipe.tasks.python import vision

# from model_utils import load_har_model, DISPLAY_NAME, RISK_ACTIVITIES
# from history_db  import save_history, get_history, init_history_db

# # ── Init ──
# app = FastAPI(title="HAR AI API")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# init_history_db()

# # ── Load model once at startup ──
# print("Loading HAR model...")
# MODEL   = load_har_model("models/activity_model.keras")
# CLASSES = np.load("classes.npy", allow_pickle=True)
# print(f"Model loaded — classes: {list(CLASSES)}")

# # ── MediaPipe ──
# base_options = mp_python.BaseOptions(model_asset_path="pose_landmarker.task")
# options      = vision.PoseLandmarkerOptions(base_options=base_options)
# LANDMARKER   = vision.PoseLandmarker.create_from_options(options)

# # ── Config ──
# SEQ_LEN           = 60
# CONFIDENCE_THRESH = 0.80
# SMOOTH_WINDOW     = 20
# MIN_VOTE_RATIO    = 0.65

# PER_CLASS_THRESH = {
#     "Drinking": 0.90, "drinking": 0.90,
#     "exercise": 0.85, "fighting": 0.85,
#     "eating":   0.83, "Eating":   0.83,
#     "no_activity": 0.70, "no": 0.70,
# }

# # ── Per-user state buffers ──
# # Each user gets their own frame_buffer and pred_buffer
# user_buffers: dict = {}

# def get_user_buffer(username: str):
#     if username not in user_buffers:
#         user_buffers[username] = {
#             "frames": deque(maxlen=SEQ_LEN),
#             "preds":  deque(maxlen=SMOOTH_WINDOW),
#             "last_save": 0.0,
#             "last_label": "Warming up...",
#             "last_conf": 0.0,
#         }
#     return user_buffers[username]


# def normalize_frame(frame: np.ndarray) -> np.ndarray:
#     out   = frame.copy()
#     hip_l = frame[23*4:23*4+3]
#     hip_r = frame[24*4:24*4+3]
#     hip_c = (hip_l + hip_r) / 2.0
#     sh_l  = frame[11*4:11*4+3]
#     sh_r  = frame[12*4:12*4+3]
#     scale = np.linalg.norm(sh_l - sh_r) + 1e-6
#     for j in range(33):
#         idx = j * 4
#         out[idx:idx+3] = (frame[idx:idx+3] - hip_c) / scale
#     return out


# def zscore_sequence(seq: np.ndarray) -> np.ndarray:
#     mean = np.mean(seq)
#     std  = np.std(seq)
#     if std < 1e-6:
#         return seq
#     return (seq - mean) / (std + 1e-6)


# def extract_keypoints(result):
#     if not result.pose_landmarks:
#         return None
#     lms      = result.pose_landmarks[0]
#     critical = [11, 12, 23, 24]
#     for idx in critical:
#         if lms[idx].visibility < 0.5:
#             return None
#     kp = []
#     for lm in lms:
#         kp.extend([lm.x, lm.y, lm.z, lm.visibility])
#     return np.array(kp, dtype=np.float32)


# @app.post("/predict")
# async def predict(request: Request):
#     """
#     Accepts: { "frame": "<base64 jpg>", "username": "mihir" }
#     Returns: { "activity": "Eating", "confidence": 0.91, "pose_valid": true }
#     """
#     try:
#         data     = await request.json()
#         username = data.get("username", "unknown")
#         frame_b64= data.get("frame", "")

#         if not frame_b64:
#             return JSONResponse({"activity": None, "confidence": 0, "pose_valid": False})

#         # Decode base64 frame
#         img_bytes = base64.b64decode(frame_b64.split(",")[-1])
#         img_array = np.frombuffer(img_bytes, dtype=np.uint8)
#         img_bgr   = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

#         if img_bgr is None:
#             return JSONResponse({"activity": None, "confidence": 0, "pose_valid": False})

#         # MediaPipe pose detection
#         rgb    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
#         mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
#         result = LANDMARKER.detect(mp_img)
#         kp     = extract_keypoints(result)

#         buf = get_user_buffer(username)

#         if kp is None:
#             # Body not fully in frame — clear buffers
#             buf["frames"].clear()
#             buf["preds"].clear()
#             buf["last_label"] = "Show full body..."
#             buf["last_conf"]  = 0.0
#             return JSONResponse({
#                 "activity":   None,
#                 "label":      "Show full body...",
#                 "confidence": 0.0,
#                 "pose_valid": False,
#             })

#         buf["frames"].append(normalize_frame(kp))

#         # Predict when buffer is full
#         if len(buf["frames"]) == SEQ_LEN:
#             seq_raw  = np.array(buf["frames"])
#             seq_norm = zscore_sequence(seq_raw)
#             seq      = seq_norm[np.newaxis, ...]
#             probs    = MODEL.predict(seq, verbose=0)[0]
#             idx      = int(np.argmax(probs))
#             conf     = float(probs[idx])
#             buf["preds"].append((idx, conf))

#             if len(buf["preds"]) >= 3:
#                 idx_counts           = Counter(p[0] for p in buf["preds"])
#                 best_idx, vote_count = idx_counts.most_common(1)[0]
#                 avg_conf             = float(np.mean([p[1] for p in buf["preds"] if p[0] == best_idx]))
#                 raw_label            = CLASSES[best_idx]
#                 threshold            = PER_CLASS_THRESH.get(raw_label, CONFIDENCE_THRESH)
#                 vote_ratio           = vote_count / len(buf["preds"])

#                 if avg_conf >= threshold and vote_ratio >= MIN_VOTE_RATIO:
#                     display = DISPLAY_NAME.get(raw_label, raw_label)
#                     buf["last_label"] = display
#                     buf["last_conf"]  = avg_conf

#                     # Save to DB every 3 seconds
#                     import time
#                     now = time.time()
#                     if now - buf["last_save"] >= 3.0:
#                         save_history(raw_label, avg_conf, username=username)
#                         buf["last_save"] = now
#                 else:
#                     buf["last_label"] = "..."
#                     buf["last_conf"]  = avg_conf

#         return JSONResponse({
#             "activity":   buf["last_label"],
#             "confidence": buf["last_conf"],
#             "pose_valid": True,
#             "is_risk":    buf["last_label"] in RISK_ACTIVITIES,
#         })

#     except Exception as e:
#         return JSONResponse({"error": str(e), "activity": None, "confidence": 0}, status_code=500)


# @app.get("/latest_activity")
# async def latest_activity(username: str = "unknown"):
#     """Poll latest activity for a user — called by browser every 2s."""
#     buf = get_user_buffer(username)
#     raw = get_history(username=username)
#     total = len(raw)
#     return JSONResponse({
#         "activity":      buf["last_label"],
#         "confidence":    buf["last_conf"],
#         "total_records": total,
#     })


# @app.get("/health")
# async def health():
#     return {"status": "ok", "model": "loaded", "classes": list(CLASSES)}

"""
api.py — HAR AI Platform
FastAPI backend: accepts frames from browser, runs pose + model, returns activity.
Also handles user registration from Vercel landing page.
Run: uvicorn api:app --host 0.0.0.0 --port 8000
"""
import os, io, cv2, base64, time, numpy as np
from collections import deque, Counter
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from model_utils import load_har_model, DISPLAY_NAME, RISK_ACTIVITIES
from history_db import (
    save_history,
    get_history,
    init_history_db,
    register_user,
    update_last_seen
)

app = FastAPI(title="HAR AI API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
init_history_db()

# ── Load model once ──
print("Loading HAR model for API...")
MODEL   = load_har_model("models/activity_model.keras")
CLASSES = np.load("classes.npy", allow_pickle=True)
print(f"API ready — {len(CLASSES)} classes")

# ── MediaPipe ──
_base = mp_python.BaseOptions(model_asset_path="pose_landmarker.task")
_opts = vision.PoseLandmarkerOptions(base_options=_base)
LAND  = vision.PoseLandmarker.create_from_options(_opts)

SEQ_LEN=60; CONF=0.80; SMOOTH=20; VOTE=0.65
PER_CLASS={"Drinking":0.90,"drinking":0.90,"exercise":0.85,"fighting":0.85,
           "eating":0.83,"Eating":0.83,"no_activity":0.70,"no":0.70}

# Per-user state
BUFFERS: dict = {}

def buf(u):
    if u not in BUFFERS:
        BUFFERS[u]={"frames":deque(maxlen=SEQ_LEN),"preds":deque(maxlen=SMOOTH),
                    "last_save":0.0,"label":"...","conf":0.0}
    return BUFFERS[u]

def norm_frame(f):
    out=f.copy()
    hc=(f[23*4:23*4+3]+f[24*4:24*4+3])/2
    sc=np.linalg.norm(f[11*4:11*4+3]-f[12*4:12*4+3])+1e-6
    for j in range(33):
        i=j*4; out[i:i+3]=(f[i:i+3]-hc)/sc
    return out

def zscore(seq):
    s=np.std(seq); return seq if s<1e-6 else (seq-np.mean(seq))/(s+1e-6)

def keypoints(result):
    if not result.pose_landmarks: return None
    lms=result.pose_landmarks[0]
    for i in [11,12,23,24]:
        if lms[i].visibility<0.5: return None
    return np.array([v for lm in lms for v in [lm.x,lm.y,lm.z,lm.visibility]],dtype=np.float32)


@app.post("/register")
async def register(request: Request):
    """Called by Vercel form — saves name+mobile to DB."""
    try:
        d = await request.json()
        name   = d.get("name","").strip()
        mobile = d.get("mobile","").strip()
        if name and mobile:
            register_user(name, mobile)
            return JSONResponse({"status":"ok","message":f"Registered {name}"})
        return JSONResponse({"status":"error","message":"Missing name or mobile"},status_code=400)
    except Exception as e:
        return JSONResponse({"status":"error","message":str(e)},status_code=500)


@app.post("/predict")
async def predict(request: Request):
    """Accepts base64 frame + username + mobile, returns activity."""
    try:
        d        = await request.json()
        username = d.get("username","unknown")
        mobile   = d.get("mobile","")
        frame_b64= d.get("frame","")
        if not frame_b64:
            return JSONResponse({"activity":None,"confidence":0,"pose_valid":False})

        img = cv2.imdecode(np.frombuffer(base64.b64decode(frame_b64.split(",")[-1]),np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return JSONResponse({"activity":None,"confidence":0,"pose_valid":False})

        rgb    = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        kp     = keypoints(LAND.detect(mp_img))
        b      = buf(username)

        if kp is None:
            b["frames"].clear(); b["preds"].clear()
            b["label"]="Show full body..."; b["conf"]=0.0
            return JSONResponse({"activity":None,"label":"Show full body...","confidence":0.0,"pose_valid":False})

        b["frames"].append(norm_frame(kp))

        if len(b["frames"])==SEQ_LEN:
            probs = MODEL.predict(zscore(np.array(b["frames"]))[np.newaxis,...],verbose=0)[0]
            idx   = int(np.argmax(probs))
            b["preds"].append((idx,float(probs[idx])))

            if len(b["preds"])>=3:
                best,vc = Counter(p[0] for p in b["preds"]).most_common(1)[0]
                ac      = float(np.mean([p[1] for p in b["preds"] if p[0]==best]))
                rl      = CLASSES[best]
                thr     = PER_CLASS.get(rl,CONF)
                if ac>=thr and vc/len(b["preds"])>=VOTE:
                    b["label"] = DISPLAY_NAME.get(rl,rl)
                    b["conf"]  = ac
                    now = time.time()
                    if now-b["last_save"]>=3.0:
                        save_history(rl, ac, username=username, mobile=mobile)
                        if mobile: update_last_seen(mobile)
                        b["last_save"]=now
                else:
                    b["label"]="..."; b["conf"]=ac

        total = len(get_history(mobile=mobile)) if mobile else 0
        return JSONResponse({"activity":b["label"],"confidence":b["conf"],
                             "pose_valid":True,"is_risk":b["label"] in RISK_ACTIVITIES,
                             "total_records":total})
    except Exception as e:
        return JSONResponse({"error":str(e),"activity":None,"confidence":0},status_code=500)


@app.get("/latest_activity")
async def latest(username: str="unknown"):
    b = buf(username)
    raw = get_history(username=username)
    return JSONResponse({"activity":b["label"],"confidence":b["conf"],"total_records":len(raw)})


@app.get("/health")
async def health():
    return {"status":"ok","classes":list(CLASSES)}