import streamlit as st  # type: ignore
from medication_tracker import top_nav_bar


# --------------------------
# USER INFO / PROFILE PAGE
# --------------------------
def user_info_page():
    """
    Displays and allows editing of the current user's profile information
    in a clean Account Settings layout.
    """

    # Top navigation (UNCHANGED)
    top_nav_bar("User Profile & Info")
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

    # --------------------------
    # PAGE TITLE
    # --------------------------
    st.markdown("## Personal Information")
    st.write("")

    # --------------------------
    # MAIN LAYOUT
    # --------------------------
    left_col, right_col = st.columns([1, 3])

    # --------------------------
    # PROFILE IMAGE
    # --------------------------
    with left_col:
        st.write("")
        st.markdown("<div class='profile-img' style='text-align:center;'>", unsafe_allow_html=True)
        st.image("assets/js.jpg", width=300)

        st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------
    # USER INFO FORM
    # --------------------------
    with right_col:
        st.write("")
        st.write("")

        # Initialize edit mode if not present
        if "edit_mode" not in st.session_state:
            st.session_state.edit_mode = False

        # Only show form if in edit mode or display read-only
        if st.session_state.edit_mode:
            email = st.text_input(
                "Email address",
                value=current_email,
                disabled=True  # Email always disabled
            )

            first_name = st.text_input(
                "First name",
                value=user_data.get("first_name", ""),
                disabled=False
            )

            last_name = st.text_input(
                "Last name",
                value=user_data.get("last_name", ""),
                disabled=False
            )

            age = st.text_input(
                "Age",
                value=user_data.get("age", ""),
                disabled=False
            )

            gender = st.text_input(
                "Gender",
                value=user_data.get("gender", ""),
                disabled=False
            )

            st.write("")

            # --------------------------
            # SAVE BUTTON (ALIGNED BOTTOM-RIGHT)
            # --------------------------
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Save Changes"):
                    st.session_state.users[current_email]["first_name"] = first_name
                    st.session_state.users[current_email]["last_name"] = last_name
                    st.session_state.users[current_email]["age"] = age
                    st.session_state.users[current_email]["gender"] = gender

                    st.success("Profile updated successfully!")
                    # Reset edit mode after save to display read-only
                    st.session_state.edit_mode = False
        else:
            # Display read-only information
            st.write(f"**Email address:** {current_email}")
            st.write(f"**First name:** {user_data.get('first_name', '')}")
            st.write(f"**Last name:** {user_data.get('last_name', '')}")
            st.write(f"**Age:** {user_data.get('age', '')}")
            st.write(f"**Gender:** {user_data.get('gender', '')}")

            st.write("")

            # --------------------------
            # EDIT BUTTON (ALIGNED BOTTOM-RIGHT)
            # --------------------------
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Edit Profile"):
                    st.session_state.edit_mode = True

    # --------------------------
    # FOOTER NOTE
    # --------------------------
    st.write("---")
    st.info("Note: This profile information was saved during the signup process.")

