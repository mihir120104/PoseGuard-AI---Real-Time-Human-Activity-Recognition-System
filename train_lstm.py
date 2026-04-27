"""
train_lstm.py  —  Production
CNN + BiLSTM + Attention model training with 5-fold cross-validation.

Run: python train_lstm.py
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Conv1D, Bidirectional, LSTM,
    Dense, Dropout, BatchNormalization,
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, Callback
from tensorflow.keras.losses import CategoricalCrossentropy
from tensorflow.keras.utils import to_categorical, register_keras_serializable
from sklearn.model_selection import StratifiedKFold
from sklearn.utils.class_weight import compute_class_weight

# ── Import shared SoftAttention — single source of truth ──
from model_utils import SoftAttention

# ─────────────────────────────────────────
# Load data
# ─────────────────────────────────────────
X       = np.load("features.npy")
y       = np.load("labels.npy")
classes = np.load("classes.npy", allow_pickle=True)

print("=" * 55)
print("  HAR MODEL TRAINING")
print("=" * 55)
print(f"  Dataset     : {X.shape}")
print(f"  Classes ({len(classes)}) : {list(classes)}")

NUM_CLASSES       = len(classes)
SEQ_LEN, FEAT_DIM = X.shape[1], X.shape[2]


# ─────────────────────────────────────────
# Cosine LR warm-up schedule
# ─────────────────────────────────────────
class WarmupCosineSchedule(Callback):
    def __init__(self, base_lr: float, warmup_epochs: int, total_epochs: int):
        super().__init__()
        self.base_lr       = base_lr
        self.warmup_epochs = warmup_epochs
        self.total_epochs  = total_epochs

    def on_epoch_begin(self, epoch: int, logs=None):
        if epoch < self.warmup_epochs:
            lr = self.base_lr * (epoch + 1) / self.warmup_epochs
        else:
            progress = (epoch - self.warmup_epochs) / (self.total_epochs - self.warmup_epochs)
            lr = self.base_lr * 0.5 * (1.0 + np.cos(np.pi * progress))
        self.model.optimizer.learning_rate = float(lr)
        print(f"  LR = {lr:.2e}", end="  ")


# ─────────────────────────────────────────
# Model builder
# ─────────────────────────────────────────
def build_model(seq_len: int, feat_dim: int, num_classes: int) -> Model:
    inp = Input(shape=(seq_len, feat_dim))

    # Conv1D feature extractor
    x = Conv1D(64,  kernel_size=3, activation="relu", padding="same")(inp)
    x = BatchNormalization()(x)
    x = Conv1D(128, kernel_size=3, activation="relu", padding="same")(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)

    # Bidirectional LSTM
    x = Bidirectional(LSTM(128, return_sequences=True))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    x = Bidirectional(LSTM(64, return_sequences=True))(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)

    # Attention
    x = SoftAttention()(x)

    # Classifier
    x   = Dense(128, activation="relu")(x)
    x   = Dropout(0.4)(x)
    out = Dense(num_classes, activation="softmax")(x)

    return Model(inputs=inp, outputs=out)


# ─────────────────────────────────────────
# Training config
# ─────────────────────────────────────────
EPOCHS     = 80
BATCH_SIZE = 16
BASE_LR    = 1e-3
N_FOLDS    = 5

y_cat = to_categorical(y, NUM_CLASSES)
skf   = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)
os.makedirs("models", exist_ok=True)

fold_scores  = []
best_val_acc = 0.0

# ─────────────────────────────────────────
# 5-Fold Cross-Validation loop
# ─────────────────────────────────────────
for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    print(f"\n{'='*55}")
    print(f"  FOLD {fold+1}/{N_FOLDS}")
    print(f"{'='*55}")

    X_train, X_val = X[train_idx], X[val_idx]
    y_train, y_val = y_cat[train_idx], y_cat[val_idx]

    cw = compute_class_weight("balanced",
                              classes=np.unique(y[train_idx]),
                              y=y[train_idx])
    class_weights = dict(enumerate(cw))

    model = build_model(SEQ_LEN, FEAT_DIM, NUM_CLASSES)
    model.compile(
        optimizer=Adam(learning_rate=BASE_LR),
        loss=CategoricalCrossentropy(label_smoothing=0.1),
        metrics=["accuracy"],
    )

    if fold == 0:
        model.summary()

    callbacks = [
        EarlyStopping(patience=12, restore_best_weights=True, monitor="val_accuracy"),
        ModelCheckpoint(
            f"models/fold_{fold+1}_best.keras",
            save_best_only=True, monitor="val_accuracy", verbose=0,
        ),
        WarmupCosineSchedule(BASE_LR, warmup_epochs=5, total_epochs=EPOCHS),
    ]

    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1,
    )

    val_acc = max(history.history["val_accuracy"])
    fold_scores.append(val_acc)
    print(f"\n  Fold {fold+1} best val accuracy: {val_acc*100:.2f}%")

    if val_acc > best_val_acc:
        best_val_acc = val_acc
        model.save("models/activity_model.keras")
        print(f"  ✅ New best model saved  (val_acc = {val_acc*100:.2f}%)")

# ─────────────────────────────────────────
# Summary
# ─────────────────────────────────────────
print(f"\n{'='*55}")
print("  CROSS-VALIDATION RESULTS")
print(f"{'='*55}")
for i, s in enumerate(fold_scores):
    print(f"  Fold {i+1}: {s*100:.2f}%")
print(f"  Mean : {np.mean(fold_scores)*100:.2f}%  ±  {np.std(fold_scores)*100:.2f}%")
print(f"  Best model → models/activity_model.keras  ({best_val_acc*100:.2f}%)")
print(f"{'='*55}")