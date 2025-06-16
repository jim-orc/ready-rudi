import streamlit as st

from app.admin import admin_view
from app.client import client_view

# Import app modules
from app.results import results_view

# Set page configuration
st.set_page_config(
    page_title="Ready Rudi Assessment Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Set up the sidebar navigation
    st.sidebar.title("Ready Rudi")
    st.sidebar.subheader("Assessment Tool")
    
    # Navigation options
    app_mode = st.sidebar.radio(
        "Select Mode:",
        options=["Client Assessment", "Results Dashboard", "Admin Panel"],
        index=0
    )
    
    # Display the selected view
    if app_mode == "Client Assessment":
        client_view()
    elif app_mode == "Admin Panel":
        admin_view()
    elif app_mode == "Results Dashboard":
        results_view()

if __name__ == "__main__":
    main()
