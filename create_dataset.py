"""
create_dataset.py  —  Production
Loads pose .npy files from pose_data/, filters, normalizes, shuffles,
and saves features.npy / labels.npy / classes.npy.

Run: python create_dataset.py
"""

import numpy as np
import os
from collections import Counter

# ─────────────────────────────────────────
# Config
# ─────────────────────────────────────────
SEQ_LEN    = 60
FEATURE_DIM = 132
MIN_SAMPLES = 10   # drop classes with fewer samples than this
DATA_PATH  = "pose_data"

X, y = [], []

# ─────────────────────────────────────────
# Load class list
# ─────────────────────────────────────────
all_files = [f for f in os.listdir(DATA_PATH) if f.endswith(".npy")]
if not all_files:
    raise FileNotFoundError(f"No .npy files found in '{DATA_PATH}'. Run extract_pose.py first.")

# Class name = everything before the first underscore+digit
raw_classes = []
for f in all_files:
    parts = f.replace(".npy","").split("_")
    # Find where the numeric index starts
    for i, p in enumerate(parts):
        if p.lstrip("-").isdigit():
            raw_classes.append("_".join(parts[:i]))
            break
    else:
        raw_classes.append(parts[0])

classes    = sorted(set(raw_classes))
class_map  = {c: i for i, c in enumerate(classes)}
print(f"Detected Classes: {classes}")

# ─────────────────────────────────────────
# Load sequences
# ─────────────────────────────────────────
skipped = 0

for fname in all_files:
    fpath = os.path.join(DATA_PATH, fname)

    try:
        seq = np.load(fpath)
    except Exception:
        skipped += 1
        continue

    if seq is None or len(seq) == 0:
        skipped += 1
        continue

    if seq.ndim != 2 or seq.shape[1] != FEATURE_DIM:
        skipped += 1
        continue

    # Z-score normalization (per sequence)
    mean = np.mean(seq)
    std  = np.std(seq)
    if std < 1e-6:
        skipped += 1
        continue
    seq = (seq - mean) / (std + 1e-6)

    # Fix length to SEQ_LEN
    if len(seq) >= SEQ_LEN:
        seq = seq[:SEQ_LEN]
    else:
        pad = np.zeros((SEQ_LEN - len(seq), FEATURE_DIM), dtype=np.float32)
        seq = np.vstack([seq, pad])

    # Determine class from filename
    parts = fname.replace(".npy","").split("_")
    label = None
    for i, p in enumerate(parts):
        if p.lstrip("-").isdigit():
            label = "_".join(parts[:i])
            break
    if label is None:
        label = parts[0]

    if label not in class_map:
        skipped += 1
        continue

    X.append(seq)
    y.append(class_map[label])

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)

print(f"\nBefore Filtering: {X.shape}")
print(f"Skipped Files   : {skipped}")

# ─────────────────────────────────────────
# Print class distribution before filtering
# ─────────────────────────────────────────
counts = Counter(y)
print("\nClass Distribution BEFORE filtering:")
for cls_idx, count in sorted(counts.items()):
    print(f"  {classes[cls_idx]}: {count}")

# ─────────────────────────────────────────
# Filter weak classes
# ─────────────────────────────────────────
keep_X, keep_y = [], []
for xi, yi in zip(X, y):
    if counts[yi] >= MIN_SAMPLES:
        keep_X.append(xi)
        keep_y.append(yi)

X = np.array(keep_X, dtype=np.float32)
y = np.array(keep_y, dtype=np.int32)

print(f"\nAfter Filtering: {X.shape}")

# ─────────────────────────────────────────
# Remap class indices to be contiguous
# ─────────────────────────────────────────
unique_old = sorted(set(y))
new_map    = {old: new for new, old in enumerate(unique_old)}
y          = np.array([new_map[i] for i in y], dtype=np.int32)
classes    = [classes[i] for i in unique_old]

counts2 = Counter(y)
print("\nClass Distribution AFTER filtering:")
for cls_idx, count in sorted(counts2.items()):
    print(f"  {classes[cls_idx]}: {count}")

# ─────────────────────────────────────────
# Shuffle
# ─────────────────────────────────────────
idx = np.arange(len(X))
np.random.shuffle(idx)
X = X[idx]
y = y[idx]

# ─────────────────────────────────────────
# Save
# ─────────────────────────────────────────
np.save("features.npy", X)
np.save("labels.npy",   y)
np.save("classes.npy",  np.array(classes))

print(f"\n✅ FINAL DATASET READY")
print(f"   Shape  : {X.shape}")
print(f"   Classes: {classes}")