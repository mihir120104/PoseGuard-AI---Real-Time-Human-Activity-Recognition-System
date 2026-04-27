"""
test_model.py  —  Production
Evaluates the trained HAR model on a held-out test set.
Saves confusion.npy, metrics.txt, metrics_detailed.txt.

Run: python test_model.py
"""

import numpy as np
from sklearn.metrics import (
    accuracy_score, classification_report, f1_score,
    confusion_matrix, top_k_accuracy_score,
)
from sklearn.model_selection import train_test_split

# ── Import shared components — single source of truth ──
from model_utils import SoftAttention, load_har_model, DISPLAY_NAME

# ─────────────────────────────────────────
# Load data
# ─────────────────────────────────────────
X       = np.load("features.npy")
y       = np.load("labels.npy")
classes = np.load("classes.npy", allow_pickle=True)

print("=" * 55)
print("  HAR MODEL EVALUATION")
print("=" * 55)
print(f"  Dataset shape  : {X.shape}")
print(f"  Classes ({len(classes)})   : {list(classes)}")

# ─────────────────────────────────────────
# Split — same seed as training
# ─────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\n  Train samples  : {len(X_train)}")
print(f"  Test  samples  : {len(X_test)}")

# ─────────────────────────────────────────
# Load model
# ─────────────────────────────────────────
model = load_har_model("models/activity_model.keras")
print(f"\n  Model loaded   : models/activity_model.keras")
print(f"  Input shape    : {model.input_shape}")
print(f"  Output shape   : {model.output_shape}")

# ─────────────────────────────────────────
# Predict
# ─────────────────────────────────────────
print("\n  Running predictions...")
probs  = model.predict(X_test, verbose=0)
y_pred = np.argmax(probs, axis=1)
y_conf = np.max(probs, axis=1)

# ─────────────────────────────────────────
# Overall metrics
# ─────────────────────────────────────────
acc    = accuracy_score(y_test, y_pred)
f1_w   = f1_score(y_test, y_pred, average="weighted")
f1_mac = f1_score(y_test, y_pred, average="macro")
top2   = top_k_accuracy_score(y_test, probs, k=min(2, len(classes)))

print("\n" + "=" * 55)
print("  OVERALL METRICS")
print("=" * 55)
print(f"  Accuracy          : {acc*100:.2f}%")
print(f"  Weighted F1       : {f1_w*100:.2f}%   ← Final F1 score")
print(f"  Macro F1          : {f1_mac*100:.2f}%")
print(f"  Top-2 Accuracy    : {top2*100:.2f}%")
print(f"  Avg Confidence    : {y_conf.mean()*100:.1f}%")

# ─────────────────────────────────────────
# Per-class metrics
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("  PER-CLASS METRICS")
print("=" * 55)
cm = confusion_matrix(y_test, y_pred)
print(f"  {'Class':<22} {'Precision':>10} {'Recall':>9} {'F1':>8} {'Support':>9} {'Avg Conf':>10}")
print("  " + "-" * 72)

per_class_stats = {}
for i, cls in enumerate(classes):
    tp      = cm[i, i]
    fn      = cm[i, :].sum() - tp
    fp      = cm[:, i].sum() - tp
    prec    = tp / (tp + fp + 1e-8)
    rec     = tp / (tp + fn + 1e-8)
    f1c     = 2 * prec * rec / (prec + rec + 1e-8)
    support = int(cm[i, :].sum())
    mask    = (y_pred == i)
    avg_c   = float(y_conf[mask].mean()) if mask.sum() > 0 else 0.0
    flag    = "  ⚠" if f1c < 0.70 else ""
    display = DISPLAY_NAME.get(cls, cls)
    print(f"  {display:<22} {prec:>10.3f} {rec:>9.3f} {f1c:>8.3f} {support:>9} {avg_c*100:>9.1f}%{flag}")
    per_class_stats[cls] = dict(
        precision=round(float(prec), 4), recall=round(float(rec), 4),
        f1=round(float(f1c), 4), support=support, avg_conf=round(avg_c, 4)
    )

# ─────────────────────────────────────────
# Full classification report
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("  CLASSIFICATION REPORT")
print("=" * 55)
display_names = [DISPLAY_NAME.get(c, c) for c in classes]
report = classification_report(y_test, y_pred, target_names=display_names, digits=4)
print(report)

# ─────────────────────────────────────────
# Confusion matrix (text)
# ─────────────────────────────────────────
print("=" * 55)
print("  CONFUSION MATRIX  (rows=actual, cols=predicted)")
print("=" * 55)
col_w = 14
hrow  = " " * 22
for cls in classes:
    hrow += DISPLAY_NAME.get(cls, cls)[:col_w-1].rjust(col_w)
print(hrow)
print("-" * (22 + col_w * len(classes)))
for i, cls in enumerate(classes):
    row = DISPLAY_NAME.get(cls, cls)[:20].ljust(22)
    for j in range(len(classes)):
        val    = cm[i, j]
        marker = f"[{val}]" if i == j else str(val)
        row   += marker.rjust(col_w)
    print(row)

# ─────────────────────────────────────────
# Misclassification analysis
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("  TOP MISCLASSIFICATIONS")
print("=" * 55)
errors = [
    (cm[i, j], classes[i], classes[j])
    for i in range(len(classes))
    for j in range(len(classes))
    if i != j and cm[i, j] > 0
]
errors.sort(reverse=True)
if errors:
    print(f"  {'Count':>6}  {'Actual':<24} → Predicted")
    print("  " + "-" * 52)
    for count, actual, predicted in errors[:10]:
        row_total = cm[np.where(np.array(classes) == actual)[0][0], :].sum()
        pct = count / row_total * 100
        act_disp  = DISPLAY_NAME.get(actual, actual)
        pred_disp = DISPLAY_NAME.get(predicted, predicted)
        print(f"  {count:>6}  {act_disp:<24} → {pred_disp}  ({pct:.0f}%)")
else:
    print("  No misclassifications!")

# ─────────────────────────────────────────
# Confidence analysis
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("  CONFIDENCE ANALYSIS")
print("=" * 55)
correct_mask = (y_pred == y_test)
wrong_mask   = ~correct_mask
if correct_mask.sum() > 0:
    print(f"  Correct : {correct_mask.sum():>4}  avg conf = {y_conf[correct_mask].mean()*100:.1f}%")
if wrong_mask.sum() > 0:
    print(f"  Wrong   : {wrong_mask.sum():>4}  avg conf = {y_conf[wrong_mask].mean()*100:.1f}%")

print("\n  Confidence buckets:")
prev = 0.0
for t in [0.50, 0.65, 0.75, 0.85, 0.95, 1.01]:
    bucket = (y_conf >= prev) & (y_conf < t)
    if bucket.sum() > 0:
        b_acc = accuracy_score(y_test[bucket], y_pred[bucket])
        print(f"    {prev:.0%} – {min(t,1.0):.0%}  :  {bucket.sum():>4} samples  acc = {b_acc*100:.1f}%")
    prev = t

# ─────────────────────────────────────────
# Weak class diagnostics
# ─────────────────────────────────────────
weak = [cls for cls, s in per_class_stats.items() if s["f1"] < 0.70]
if weak:
    print("\n" + "=" * 55)
    print("  ⚠  WEAK CLASSES (F1 < 0.70)")
    print("=" * 55)
    for cls in weak:
        s = per_class_stats[cls]
        print(f"  {DISPLAY_NAME.get(cls,cls)}")
        print(f"    F1={s['f1']:.3f}  Prec={s['precision']:.3f}  Rec={s['recall']:.3f}")
        if s["recall"] < s["precision"]:
            print(f"    → Low recall: collect more '{cls}' training data.")
        else:
            print(f"    → Low precision: '{cls}' confused with another class.")

# ─────────────────────────────────────────
# Save outputs
# ─────────────────────────────────────────
np.save("confusion.npy", cm)

with open("metrics.txt", "w") as f:
    f.write(f"Accuracy:{acc}\n")
    f.write(f"F1:{f1_w}\n")
    f.write(f"F1_macro:{f1_mac}\n")
    f.write(f"Top2_accuracy:{top2}\n")
    f.write(f"Avg_confidence:{float(y_conf.mean())}\n")
    f.write(f"Correct_samples:{int(correct_mask.sum())}\n")
    f.write(f"Wrong_samples:{int(wrong_mask.sum())}\n")

with open("metrics_detailed.txt", "w") as f:
    f.write("HAR MODEL — DETAILED METRICS\n")
    f.write("=" * 55 + "\n\n")
    f.write(f"Accuracy    : {acc*100:.2f}%\n")
    f.write(f"Weighted F1 : {f1_w*100:.2f}%\n")
    f.write(f"Macro F1    : {f1_mac*100:.2f}%\n")
    f.write(f"Top-2 Acc   : {top2*100:.2f}%\n\n")
    f.write("Per-Class:\n")
    for cls, s in per_class_stats.items():
        f.write(f"  {DISPLAY_NAME.get(cls,cls):<22} F1={s['f1']:.3f}  "
                f"Prec={s['precision']:.3f}  Rec={s['recall']:.3f}  "
                f"Support={s['support']}\n")
    f.write("\nClassification Report:\n")
    f.write(report)

print("\n" + "=" * 55)
print("  FILES SAVED")
print("=" * 55)
print("  confusion.npy        → confusion matrix")
print("  metrics.txt          → used by app.py dashboard")
print("  metrics_detailed.txt → full per-class breakdown")
print(f"\n  ★  FINAL F1  →  {f1_w*100:.2f}%  (weighted, held-out test set)")
print("=" * 55)