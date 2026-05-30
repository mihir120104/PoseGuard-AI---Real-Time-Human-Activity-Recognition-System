"""
model_utils.py
Shared model components imported by train_lstm.py, test_model.py, real_time.py, and app.py.
Never define SoftAttention in more than one place — always import from here.
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Layer
from tensorflow.keras.utils import register_keras_serializable
from tensorflow.keras.models import load_model as _keras_load


@register_keras_serializable(package="HAR")
class SoftAttention(Layer):
    """
    Soft self-attention over the time axis.
    Input  shape : (batch, time_steps, features)
    Output shape : (batch, features)  — weighted sum over time steps
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score_dense = Dense(1, activation="tanh")

    def build(self, input_shape):
        self.score_dense.build(input_shape)
        super().build(input_shape)

    def call(self, inputs):
        score   = self.score_dense(inputs)                # (batch, T, 1)
        score   = tf.squeeze(score, axis=-1)              # (batch, T)
        weights = tf.nn.softmax(score, axis=-1)           # (batch, T)
        weights = tf.expand_dims(weights, axis=-1)        # (batch, T, 1)
        context = inputs * weights                        # (batch, T, F)
        return tf.reduce_sum(context, axis=1)             # (batch, F)

    def get_config(self):
        return super().get_config()


def load_har_model(path="models/activity_model.keras"):
    import os
    if not os.path.exists(path):
        print(f"Model not found locally — downloading from HuggingFace...")
        try:
            from huggingface_hub import hf_hub_download
            os.makedirs("models", exist_ok=True)
            hf_hub_download(
                repo_id="mihir1201/poseguard-api",
                filename="models/activity_model.keras",
                repo_type="space",
                local_dir=".",
                local_dir_use_symlinks=False
            )
            print("Model downloaded successfully")
        except Exception as e:
            print(f"Download failed: {e}")
            raise
    return _keras_load(path, custom_objects={"SoftAttention": SoftAttention})


# Display names for the camera overlay and dashboard
DISPLAY_NAME: dict = {
    "no":          "No Activity",
    "no_activity": "No Activity",
}

# Activities that trigger the red alert
RISK_ACTIVITIES: list = ["fighting", "Fighting", "falling"]