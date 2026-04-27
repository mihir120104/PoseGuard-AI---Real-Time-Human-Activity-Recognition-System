"""
collect_data.py  —  Production
Interactive webcam tool to record training videos for a chosen activity class.
Each recording saves one video file to dataset/<class_name>/.

Run: python collect_data.py
Controls:
  SPACE — start / stop recording
  N     — next recording (save current, start new)
  Q     — quit
"""

import cv2
import os
import time
import numpy as np
from datetime import datetime

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
DATASET_PATH = "dataset"
FPS          = 20
DURATION_SEC = 5       # target recording length per clip
MIN_FRAMES   = 60      # minimum frames to keep a clip

# ─────────────────────────────────────────
# Choose class
# ─────────────────────────────────────────
existing = sorted([
    d for d in os.listdir(DATASET_PATH)
    if os.path.isdir(os.path.join(DATASET_PATH, d))
]) if os.path.exists(DATASET_PATH) else []

print("\n" + "="*55)
print("  HAR DATA COLLECTION TOOL")
print("="*55)

if existing:
    print(f"\n  Existing classes:")
    for i, cls in enumerate(existing):
        n = len([f for f in os.listdir(os.path.join(DATASET_PATH, cls))
                 if f.endswith((".mp4",".avi"))])
        status = "✓ OK" if n >= 150 else f"⚠ need more ({n}/150)"
        print(f"    {i+1:2}. {cls:<20} {status}")

print(f"\n  Type a class name (existing or new):")
label = input("  Class: ").strip()

if not label:
    print("No class entered. Exiting.")
    exit()

save_dir = os.path.join(DATASET_PATH, label)
os.makedirs(save_dir, exist_ok=True)

# Count existing clips
existing_clips = [f for f in os.listdir(save_dir) if f.endswith((".mp4",".avi"))]
clip_number    = len(existing_clips)

print(f"\n  Recording class : '{label}'")
print(f"  Save directory  : {save_dir}/")
print(f"  Existing clips  : {clip_number}")
print(f"  Target          : 150+ clips")
print(f"\n  Controls:")
print(f"    SPACE — start / stop recording")
print(f"    N     — save current clip, prepare next")
print(f"    Q     — quit")
print(f"\n  Opening camera...")

# ─────────────────────────────────────────
# Camera
# ─────────────────────────────────────────
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open webcam.")

w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

recording   = False
frames      = []
saved_count = 0

def save_clip(frames_list: list, label_: str, number: int) -> bool:
    if len(frames_list) < MIN_FRAMES:
        print(f"  Clip too short ({len(frames_list)} frames < {MIN_FRAMES}). Discarded.")
        return False
    fname    = f"{label_}_{number:04d}_{datetime.now().strftime('%H%M%S')}.mp4"
    fpath    = os.path.join(save_dir, fname)
    fourcc   = cv2.VideoWriter_fourcc(*"mp4v")
    writer   = cv2.VideoWriter(fpath, fourcc, FPS, (w, h))
    for f in frames_list:
        writer.write(f)
    writer.release()
    print(f"  Saved: {fname}  ({len(frames_list)} frames)")
    return True

print(f"  Camera ready. Press SPACE to start recording.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    display = frame.copy()

    # Status bar
    bar_color = (0, 60, 200) if recording else (30, 30, 30)
    cv2.rectangle(display, (0, h-80), (w, h), bar_color, -1)

    if recording:
        frames.append(frame.copy())
        elapsed = len(frames) / FPS
        prog    = min(elapsed / DURATION_SEC, 1.0)
        bar_w   = int((w - 40) * prog)
        cv2.rectangle(display, (20, h-20), (20+bar_w, h-8), (0, 200, 100), -1)
        cv2.rectangle(display, (20, h-20), (w-20, h-8),     (80, 80, 80), 1)
        cv2.putText(display, f"RECORDING  {elapsed:.1f}s / {DURATION_SEC}s",
                    (20, h-50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 120), 2, cv2.LINE_AA)
        cv2.putText(display, f"Clip #{clip_number+1}  |  {len(frames)} frames",
                    (20, h-28), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (160, 160, 160), 1, cv2.LINE_AA)

        # Auto-stop at target duration
        if elapsed >= DURATION_SEC:
            if save_clip(frames, label, clip_number):
                saved_count += 1
                clip_number += 1
            frames = []
            recording = False
    else:
        total_clips = clip_number
        cv2.putText(display, f"Class: {label}  |  Clips: {total_clips}  |  Session saved: {saved_count}",
                    (20, h-50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (160, 160, 160), 1, cv2.LINE_AA)
        cv2.putText(display, "SPACE=Record  N=Save+Next  Q=Quit",
                    (20, h-25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (100, 100, 100), 1, cv2.LINE_AA)

    # Class label overlay
    cv2.putText(display, label, (10, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 210, 160), 2, cv2.LINE_AA)

    cv2.imshow(f"Data Collection — {label}", display)
    key = cv2.waitKey(1) & 0xFF

    if key == ord(" "):  # SPACE — toggle recording
        if not recording:
            frames    = []
            recording = True
            print(f"  Recording clip #{clip_number+1}...")
        else:
            recording = False
            if save_clip(frames, label, clip_number):
                saved_count += 1
                clip_number += 1
            frames = []

    elif key == ord("n"):  # N — save and prepare next
        if recording and frames:
            recording = False
            if save_clip(frames, label, clip_number):
                saved_count += 1
                clip_number += 1
            frames = []
        print(f"  Ready for clip #{clip_number+1}. Press SPACE to record.")

    elif key == ord("q"):  # Q — quit
        if recording and frames:
            save_clip(frames, label, clip_number)
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n{'='*55}")
print(f"  Session complete")
print(f"  Class     : {label}")
print(f"  New clips : {saved_count}")
print(f"  Total     : {clip_number}")
print(f"\n  Next steps:")
print(f"  1. python extract_pose.py")
print(f"  2. python create_dataset.py")
print(f"  3. python train_lstm.py")
print(f"{'='*55}")