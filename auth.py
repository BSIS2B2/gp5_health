import streamlit as st  # type: ignore
import time
from sample_data import go_to

# --------------------------
# AUTH ENTRY PAGE
# --------------------------
def auth_entry_page():
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)

    try:
        st.image("logo.png", width=140)
    except:
        st.markdown(
            "<div style='font-size:26px;font-weight:700;color:#0b5394;'>Healthcare App</div>",
            unsafe_allow_html=True
        )

    st.markdown("<div class='header-title'>Welcome</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtle'>Secure healthcare system</div>", unsafe_allow_html=True)

    if st.button("🔐 Login", use_container_width=True):
        go_to("login")

    if st.button("📝 Sign Up", use_container_width=True):
        go_to("signup")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# LOGIN PAGE
# --------------------------
def login_page():
    st.markdown("<div style='max-width:760px;margin:20px auto'>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Login")

    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown("<div class='center-label'>Email</div>", unsafe_allow_html=True)
        email = st.text_input("", key="login_email")

        st.markdown("<div class='center-label'>Password</div>", unsafe_allow_html=True)
        password = st.text_input("", type="password", key="login_password")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Log in", use_container_width=True):
            users = st.session_state.users
            if email in users and users[email]["password"] == password:
                prog = st.progress(0)
                for i in range(0, 101, 20):
                    prog.progress(i)
                    time.sleep(0.04)

                st.session_state.current_user = email
                st.success("Login successful!")
                go_to("dashboard")
            else:
                st.error("Incorrect email or password.")

    with col2:
        if st.button("Back", use_container_width=True):
            go_to("auth")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# SIGNUP PAGE
# --------------------------
def signup_page():
    st.markdown("<div style='max-width:760px;margin:20px auto'>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("###  Create Account")

    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown("<div class='center-label'>First Name</div>", unsafe_allow_html=True)
        first_name = st.text_input("", key="signup_firstname")

        st.markdown("<div class='center-label'>Last Name</div>", unsafe_allow_html=True)
        last_name = st.text_input("", key="signup_lastname")

        st.markdown("<div class='center-label'>Age</div>", unsafe_allow_html=True)
        age = st.number_input("", min_value=1, max_value=120, step=1, key="signup_age")

        st.markdown("<div class='center-label'>Gender</div>", unsafe_allow_html=True)
        gender = st.selectbox("", ["Male", "Female", "Other"], key="signup_gender")

        st.markdown("<div class='center-label'>Email</div>", unsafe_allow_html=True)
        email = st.text_input("", key="signup_email")

        st.markdown("<div class='center-label'>Password</div>", unsafe_allow_html=True)
        password = st.text_input("", type="password", key="signup_password")

        st.markdown("<div class='center-label'>Confirm Password</div>", unsafe_allow_html=True)
        password2 = st.text_input("", type="password", key="signup_confirm")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Sign Up", use_container_width=True):
            if not all([first_name, last_name, age, email, password, password2]):
                st.warning("Please fill all fields.")
            elif password != password2:
                st.error("Passwords do not match.")
            elif email in st.session_state.users:
                st.error("Email already exists.")
            else:
                st.session_state.users[email] = {
                    "password": password,
                    "first_name": first_name,
                    "last_name": last_name,
                    "age": age,
                    "gender": gender
                }
                st.success("Account created!")
                go_to("login")

    with col2:
        if st.button("Back", use_container_width=True):
            go_to("auth")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)