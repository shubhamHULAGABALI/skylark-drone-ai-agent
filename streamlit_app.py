import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Streamlit Cloud entrypoint — runs ui/app.py
exec(open(os.path.join(os.path.dirname(__file__), "ui", "app.py")).read())
