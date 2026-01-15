import streamlit as st  # type: ignore
import os
from medication_tracker import top_nav_bar

# --------------------------
# USER INFO / PROFILE PAGE
# --------------------------
def user_info_page():

    # Top navigation
    top_nav_bar("User Profile")
    st.write("")

    # --------------------------
    # USER VALIDATION
    # --------------------------
    if "current_user" not in st.session_state:
        st.error("No active session. Please log in again.")
        return

    current_email = st.session_state.current_user

    if "users" not in st.session_state or current_email not in st.session_state.users:
        st.error("User data not found. Please log in again.")
        return

    user_data = st.session_state.users[current_email]

    # Init edit mode
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    full_name = f"{user_data.get('first_name','')} {user_data.get('last_name','')}".strip()

    # --------------------------
    # MAIN LAYOUT
    # --------------------------
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
            st.markdown(
                f"""
                <h1 class="profile-name">{full_name}</h1>
                """,
                unsafe_allow_html=True
            )
        with col_r:
            if not st.session_state.edit_mode:
                if st.button("Edit", key="edit_top"):
                    st.session_state.edit_mode = True

        st.markdown("<hr>", unsafe_allow_html=True)

        # READ MODE
        if not st.session_state.edit_mode:
            st.markdown(
                f"""
                <div class="profile-info">
                    <p><b>Email:</b> {current_email}</p>
                    <p><b>First Name:</b> {user_data.get("first_name","")}</p>
                    <p><b>Last Name:</b> {user_data.get("last_name","")}</p>
                    <p><b>Age:</b> {user_data.get("age","")}</p>
                    <p><b>Gender:</b> {user_data.get("gender","")}</p>
                    <p><b>Status:</b> <span class="status-active">● Active</span></p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # EDIT MODE
        if st.session_state.edit_mode:
            first_name = st.text_input("First name", user_data.get("first_name", ""))
            last_name = st.text_input("Last name", user_data.get("last_name", ""))
            age = st.text_input("Age", user_data.get("age", ""))
            gender = st.text_input("Gender", user_data.get("gender", ""))

            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Save Changes", key="save_changes"):
                    user_data["first_name"] = first_name
                    user_data["last_name"] = last_name
                    user_data["age"] = age
                    user_data["gender"] = gender

                    st.session_state.edit_mode = False
                    st.success("Profile updated successfully!")

    st.markdown('</div>', unsafe_allow_html=True)  # Close profile column
