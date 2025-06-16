import os
import subprocess
import sys


def main():
    """
    Main entry point for the Ready Rudi Assessment Tool.
    Initializes the database and launches the Streamlit app.
    """
    # Initialize the database first
    print("Initializing database...")
    from init_db import init_database
    init_database()
    
    # Launch the Streamlit app
    print("Launching Streamlit app...")
    
    # Get the absolute path to streamlit_app.py
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "streamlit_app.py")
    
    # Run Streamlit
    try:
        result = subprocess.run(
            [sys.executable, "-m", "streamlit", "run", app_path],
            check=True
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error launching Streamlit app: {e}")
        return e.returncode
    except FileNotFoundError:
        print("Streamlit not found. Please install it with 'pip install streamlit'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
