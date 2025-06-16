import os
import sys

import streamlit as st

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app main function
from app.main import main

if __name__ == "__main__":
    main()
