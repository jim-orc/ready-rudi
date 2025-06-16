#!/usr/bin/env python3

"""
Runner script for the Ready Rudi Assessment Tool.
This script initializes the database and runs the Streamlit application.
"""

import subprocess
import sys


def main():
    # Initialize the database
    print("Initializing database...")
    subprocess.run([sys.executable, "init_db.py"], check=True)
    
    # Run the Streamlit app
    print("Launching Streamlit app...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)

if __name__ == "__main__":
    main()
