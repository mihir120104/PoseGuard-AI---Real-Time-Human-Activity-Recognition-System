<div align="center">

![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.18-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10-0097A7?style=flat-square)
![F1](https://img.shields.io/badge/F1_Score-99.61%25-22C55E?style=flat-square)
![Accuracy](https://img.shields.io/badge/Accuracy-99.61%25-14B8A6?style=flat-square)

# Human Activity Recognition
### CNN + BiLSTM + Attention

Real-time activity recognition from webcam using a **custom-built** deep learning model.
Classifies 7 activities with **99.61% F1 score** on a held-out test set.

*"Every movement tells a story — we decode it."*

</div>

---

## Problem Statement

Automatically identify what a person is doing from webcam video — in real time, without any manual input. The system detects 7 activities: **Drinking, Eating, Exercise, Fighting, No Activity, Typing, Writing on Board.**

**Why it is hard:**
- Eating and drinking look almost identical (both = hand to mouth) — needs sequence modeling, not single-frame classification
- Different people have different body sizes — requires normalization so the model learns activity, not height
- Real-time constraint — must run on CPU with prediction latency under 1 second

---

## What Makes This Custom-Built

The model does **not use pixels**. MediaPipe extracts 33 body joint coordinates per frame. Those coordinates are fed into a neural network designed and trained from scratch.

The `SoftAttention` class is **original code** — this layer does not exist in TensorFlow:

```python
class SoftAttention(Layer):
    def call(self, inputs):
        score   = self.score_dense(inputs)       # score each of 60 frames
        weights = tf.nn.softmax(score, axis=-1)  # normalize → sum = 1
        context = inputs * weights               # weight each frame
        return tf.reduce_sum(context, axis=1)    # 60 frames → 1 vector
```

All ~642 training videos were **self-recorded** — no external dataset used.

---

## Model Architecture

```
Input      (60, 132)   — 60 frames × 33 landmarks × 4 values
Conv1D     (60,  64)   — local motion patterns across 3-frame windows
Conv1D     (60, 128)   — deeper spatial features + BatchNorm
BiLSTM    (60, 256)   — temporal sequence, forward + backward
BiLSTM    (60, 128)   — higher-level temporal abstraction
Attention     (128)   — weights 60 frames by importance ← custom
Dense         (128)   — classification head
Softmax         (7)   — probability over 7 classes

Parameters : 497,480  |  Size : 1.90 MB  |  Device : CPU only
```

| Layer | Why chosen |
|---|---|
| Conv1D | Input is a 1D time series, not an image — finds local motion patterns |
| BiLSTM | Reads sequence forward AND backward — full temporal context |
| SoftAttention | Focuses on the most important frames, not average of all 60 |

---

## Data & Training

| Item | Value |
|---|---|
| Training data | ~642 self-recorded videos, 7 classes |
| After 4× augmentation | 2,568 sequences |
| Train / Test split | 2,054 / 514 (80/20) |
| Input per sample | 60 frames × 132 features |
| Training strategy | 5-fold cross-validation |
| Optimizer | Adam + Cosine LR warmup |
| Loss function | Categorical cross-entropy (label smoothing 0.1) |

**Augmentation** — each video → 4 variants: original, horizontal flip, gaussian noise (σ=0.005), time warp (±20%).

**Normalization** — two steps applied at both training and inference:
1. Hip-center normalization → person-size invariant
2. Z-score normalization → matches training value range at inference

---

## Results

| Metric | Score |
|---|---|
| Test Accuracy | **99.61%** |
| Weighted F1 | **99.61%** |
| Macro F1 | 99.64% |
| Top-2 Accuracy | 100.00% |
| 5-Fold CV Mean | 99.10% ± 0.29% |
| Misclassifications | 2 / 514 |
| Baseline (simple LSTM) | 73.0% |
| **Improvement** | **+26.6%** |

---

## Key Challenges Solved

**Z-score mismatch bug** — training applied z-score normalization but inference did not. Model defaulted to "Drinking" for every input. Fixed by matching the full preprocessing pipeline between training and inference.

**Hips not in frame** — hip-center normalization fails when hip landmarks are off-screen. Fixed by checking landmark visibility before accepting a frame.

**Class imbalance** — Drinking had 400 samples, Typing had 236. Fixed with balanced class weights during training and higher confidence threshold for Drinking (90%) at inference.

---

## Tech Stack

`TensorFlow 2.18` · `MediaPipe` · `Streamlit` · `NumPy` · `scikit-learn` · `SQLite` · `ReportLab` · `Render.com`

---