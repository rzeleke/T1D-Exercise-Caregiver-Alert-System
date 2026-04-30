# 🏃 T1D Exercise Caregiver Alert System

A Python-based application that automatically alerts caregivers of Type 1 Diabetes (T1D) patients before scheduled exercise sessions to prevent exercise-induced hypoglycemia.

> **Open-source project** — Built as a graduate Health Informatics capstone at George Mason University.

## The Problem
People with Type 1 Diabetes face a high risk of hypoglycemia during and after exercise due to complex interactions between insulin, activity, and glucose metabolism.

While tools like Continuous Glucose Monitors (CGMs) provide real-time data, they do not reliably anticipate exercise-related glucose drops before they occur.

As a result, patients and caregivers often react to hypoglycemia rather than prevent it, especially when physical activity is unplanned or not communicated in advance.

## What It Does
- Imports exercise sessions from Google Calendar export (.ics)
- Sends automatic SMS alerts to caregiver 30 minutes before each session
- Pre-exercise glucose check-in with six-zone clinical decision support (ADA 2026)
- Automatic caregiver SMS for high-risk glucose readings
- Session history dashboard with longitudinal trend charts

## Quick Start
```bash
git clone https://github.com/rzeleke/T1D-Alert.git
cd T1D-Alert
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Tech Stack
Python, Streamlit, pandas, SQLite, Twilio API, APScheduler, matplotlib

## GitHub
https://github.com/rzeleke/T1D-Alert