# user_info.py 
import streamlit as st # type: ignore
import pandas as pd # type: ignore
# Re-using the navigation bar from the medication tracker module
from medication_tracker import top_nav_bar 

# --- USER INFO PAGE ---
def user_info_page():
    """
    Displays the current user's personal information with high-contrast labels 
    and values for improved visibility.
    """
    top_nav_bar("User Profile & Info")
    st.write("")  # spacing

    current_email = st.session_state.current_user
    
    # 1. User check and data retrieval
    if current_email not in st.session_state.users:
        st.error("User data not found. Please log in again.")
        return

    user_data = st.session_state.users[current_email]

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### My Profile Details", unsafe_allow_html=True)
    
    # ----------------------------------
    # Prepare data
    # ----------------------------------
    
    # Map dictionary keys to display names, providing "N/A" fallback for missing data
    info_list = {
        "Email": current_email,
        "First Name": user_data.get("first_name", "N/A"),
        "Last Name": user_data.get("last_name", "N/A"),
        "Age": user_data.get("age", "N/A"),
        "Gender": user_data.get("gender", "N/A")
    }
    
    # Create two columns for a clean presentation
    col_labels, col_values = st.columns([1, 2])
    
    # Headers - Using explicit black color (#000000) for maximum contrast
    col_labels.markdown("<span style='color:#000000;'>**Field**</span>", unsafe_allow_html=True)
    col_values.markdown("<span style='color:#000000;'>**Value**</span>", unsafe_allow_html=True)
    
    col_labels.markdown("---")
    col_values.markdown("---")

    # ----------------------------------
    # Display data in a row-by-row structure
    # ----------------------------------
    for label, value in info_list.items():
        # Display the field name/Label in the first column (explicitly black)
        label_html = f"<span style='color:#000000;'>**{label}:**</span>"
        col_labels.markdown(label_html, unsafe_allow_html=True)
        
        # Display the value in the second column (explicitly black)
        value_html = f"<span style='color:#000000;'>{value}</span>"
        col_values.markdown(value_html, unsafe_allow_html=True)


    st.markdown("</div>", unsafe_allow_html=True)
    
    st.write("---")
    
    st.info("Note: This profile information was saved during the signup process.")