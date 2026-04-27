# Human Activity Recognition (HAR) using CNN + LSTM + Pose Estimation

## 📌 Project Overview
This project implements a real-time Human Activity Recognition (HAR) system using
MediaPipe Pose Estimation and Deep Learning (CNN + LSTM).
The system classifies human activities from live video or images using skeletal keypoints.

26/03/2026

This project implements a real-time Human Activity Recognition (HAR) system using MediaPipe Pose Estimation and a hybrid CNN-LSTM deep learning model. The system extracts skeletal keypoints from live video streams and analyzes temporal motion patterns to classify human activities such as walking, writing, exercise, and fighting.

It includes advanced features like real-time prediction stabilization, confidence filtering, alert detection for risky activities, and an interactive dashboard for monitoring activity history and analytics. The system is designed to be scalable and can be extended into a production-level surveillance or behavior monitoring solution.

## 🚀 Activities Detected
- Walking
- Sitting
- Running
- Fighting
- Falling

## 🧠 Methodology
1. Pose keypoints extraction using MediaPipe Pose
2. Temporal sequence generation
3. CNN + LSTM based deep learning model
4. Real-time webcam inference using OpenCV

## 🛠️ Technology Stack
- Python
- TensorFlow / Keras
- MediaPipe
- OpenCV
- NumPy
- Scikit-learn
