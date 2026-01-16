#user_info.py
import streamlit as st  # type: ignore
import os
from medication_tracker import top_nav_bar


def user_info_page():
    """Display and manage user profile information."""
    top_nav_bar("User Profile")
    st.write("")

    # Validate session
    if "current_user" not in st.session_state:
        st.error("No active session. Please log in again.")
        return

    current_email = st.session_state.current_user
    if "users" not in st.session_state or current_email not in st.session_state.users:
        st.error("User data not found. Please log in again.")
        return

    user_data = st.session_state.users[current_email]
    
    # Initialize edit mode
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()

    # Main profile layout
    st.markdown('<div class="profile-column">', unsafe_allow_html=True)
    
    col_img, col_info = st.columns([1, 3])

    # Profile Image
    with col_img:
        if os.path.exists("profile.jpg"):
            st.image("profile.jpg", width=170)
        else:
            st.markdown('<div class="avatar-circle">👤</div>', unsafe_allow_html=True)

    # Profile Info
    with col_info:
        col_l, col_r = st.columns([4, 1])
        
        with col_l:
            st.markdown(f"<h1 class='profile-name'>{full_name}</h1>", unsafe_allow_html=True)
        
        with col_r:
            if not st.session_state.edit_mode:
                if st.button("✏️ Edit", key="edit_btn"):
                    st.session_state.edit_mode = True
                    st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # Read mode display
        if not st.session_state.edit_mode:
            st.markdown(
                f"""
                <div class="profile-info">
                    <p><b>Email:</b> {current_email}</p>
                    <p><b>First Name:</b> {user_data.get('first_name', '')}</p>
                    <p><b>Last Name:</b> {user_data.get('last_name', '')}</p>
                    <p><b>Age:</b> {user_data.get('age', '')}</p>
                    <p><b>Gender:</b> {user_data.get('gender', '')}</p>
                    <p><b>Status:</b> <span class="status-active">● Active</span></p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Edit mode
        else:
            st.subheader("Edit Profile")
            first_name = st.text_input("First Name", user_data.get("first_name", ""))
            last_name = st.text_input("Last Name", user_data.get("last_name", ""))
            age = st.text_input("Age", user_data.get("age", ""))
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                 index=0 if user_data.get("gender") == "Male" else 1 if user_data.get("gender") == "Female" else 2)

            col_save, col_cancel = st.columns([1, 1])
            
            with col_save:
                if st.button("💾 Save Changes", use_container_width=True, key="save_changes"):
                    user_data["first_name"] = first_name
                    user_data["last_name"] = last_name
                    user_data["age"] = age
                    user_data["gender"] = gender
                    st.session_state.edit_mode = False
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Cancel", use_container_width=True, key="cancel_edit"):
                    st.session_state.edit_mode = False
                    st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
