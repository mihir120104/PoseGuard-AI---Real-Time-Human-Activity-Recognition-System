#!/bin/bash
# Runs FastAPI (port 8000) + Streamlit ($PORT) together on Render
uvicorn api:app --host 0.0.0.0 --port 8000 &
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0