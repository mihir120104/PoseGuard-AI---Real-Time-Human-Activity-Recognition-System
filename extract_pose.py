"""
extract_pose.py  —  Production
Extracts MediaPipe pose landmarks from video files and saves as .npy sequences.
Applies hip-center normalization + 3x data augmentation per video.

Run: python extract_pose.py
"""

import cv2
import numpy as np
import os
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
DATASET_PATH = "dataset"
SAVE_PATH    = "pose_data"
MODEL_PATH   = "pose_landmarker.task"
MIN_FRAMES   = 10

# Left/right landmark pairs for horizontal flip
FLIP_PAIRS = [
    (11,12),(13,14),(15,16),(17,18),(19,20),(21,22),
    (23,24),(25,26),(27,28),(29,30),(31,32)
]

os.makedirs(SAVE_PATH, exist_ok=True)


# ─────────────────────────────────────────
# MediaPipe setup
# ─────────────────────────────────────────
base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
options      = vision.PoseLandmarkerOptions(base_options=base_options)
landmarker   = vision.PoseLandmarker.create_from_options(options)


# ─────────────────────────────────────────
# Keypoint extraction
# ─────────────────────────────────────────
def extract_keypoints(result) -> np.ndarray:
    """Return (132,) array or zeros if no person detected."""
    if not result.pose_landmarks:
        return np.zeros(132)
    kp = []
    for lm in result.pose_landmarks[0]:
        kp.extend([lm.x, lm.y, lm.z, lm.visibility])
    return np.array(kp, dtype=np.float32)


# ─────────────────────────────────────────
# Normalization
# ─────────────────────────────────────────
def normalize_sequence(seq: np.ndarray) -> np.ndarray:
    """
    Hip-center normalization:
      - Translate so hip midpoint (avg lm 23 & 24) is (0,0,0)
      - Scale by shoulder width (dist lm 11 & 12)
    Makes the model person-size and camera-distance invariant.
    """
    out = seq.copy()
    for i, frame in enumerate(seq):
        hip_l  = frame[23*4:23*4+3]
        hip_r  = frame[24*4:24*4+3]
        hip_c  = (hip_l + hip_r) / 2.0
        sh_l   = frame[11*4:11*4+3]
        sh_r   = frame[12*4:12*4+3]
        scale  = np.linalg.norm(sh_l - sh_r) + 1e-6
        for j in range(33):
            idx = j * 4
            out[i, idx:idx+3] = (frame[idx:idx+3] - hip_c) / scale
    return out


# ─────────────────────────────────────────
# Augmentation
# ─────────────────────────────────────────
def flip_sequence(seq: np.ndarray) -> np.ndarray:
    """Horizontally mirror a pose sequence."""
    flipped = seq.copy()
    for i, frame in enumerate(seq):
        arr = frame.reshape(33, 4)
        arr[:, 0] = -arr[:, 0]
        for l, r in FLIP_PAIRS:
            arr[[l, r]] = arr[[r, l]]
        flipped[i] = arr.flatten()
    return flipped


def add_gaussian_noise(seq: np.ndarray, sigma: float = 0.005) -> np.ndarray:
    """Add small Gaussian noise to XYZ coordinates only (not visibility)."""
    noisy = seq.copy()
    for j in range(33):
        idx = j * 4
        noisy[:, idx:idx+3] += np.random.normal(0, sigma, (len(seq), 3)).astype(np.float32)
    return noisy


def time_warp(seq: np.ndarray, factor: float = None) -> np.ndarray:
    """Randomly stretch or compress sequence by ±20%, resample back to original length."""
    n = len(seq)
    if factor is None:
        factor = np.random.uniform(0.8, 1.2)
    new_len = max(int(n * factor), MIN_FRAMES)
    src_idx = np.linspace(0, n - 1, new_len)
    warped  = np.array([seq[int(round(i))] for i in src_idx])
    dst_idx = np.linspace(0, len(warped) - 1, n)
    return np.array([warped[int(round(i))] for i in dst_idx])


# ─────────────────────────────────────────
# Main extraction loop
# ─────────────────────────────────────────
total_saved   = 0
total_skipped = 0

for label in sorted(os.listdir(DATASET_PATH)):
    label_path = os.path.join(DATASET_PATH, label)
    if not os.path.isdir(label_path):
        continue

    files = [f for f in os.listdir(label_path)
             if f.lower().endswith((".mp4",".avi",".mov",".mkv",".wmv"))]

    print(f"\n[{label}] — {len(files)} videos")

    for idx, fname in enumerate(files):
        path     = os.path.join(label_path, fname)
        cap      = cv2.VideoCapture(path)
        sequence = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = landmarker.detect(mp_img)
            kp     = extract_keypoints(result)
            if np.sum(kp) > 0:
                sequence.append(kp)

        cap.release()

        if len(sequence) < MIN_FRAMES:
            print(f"  SKIP (too short: {len(sequence)} frames): {fname}")
            total_skipped += 1
            continue

        seq = np.array(sequence, dtype=np.float32)

        # Original (normalized)
        seq_norm = normalize_sequence(seq)
        np.save(os.path.join(SAVE_PATH, f"{label}_{idx}.npy"), seq_norm)

        # Augmentation 1: flip
        np.save(os.path.join(SAVE_PATH, f"{label}_{idx}_flip.npy"),
                normalize_sequence(flip_sequence(seq)))

        # Augmentation 2: noise
        np.save(os.path.join(SAVE_PATH, f"{label}_{idx}_noise.npy"),
                add_gaussian_noise(seq_norm))

        # Augmentation 3: time warp
        np.save(os.path.join(SAVE_PATH, f"{label}_{idx}_warp.npy"),
                normalize_sequence(time_warp(seq)))

        total_saved += 4
        print(f"  Saved {label}_{idx} + 3 augmentations")

print(f"\n{'='*50}")
print(f"  Extraction complete")
print(f"  Files saved  : {total_saved}")
print(f"  Files skipped: {total_skipped}")
print(f"  Output dir   : {SAVE_PATH}/")
print(f"{'='*50}")