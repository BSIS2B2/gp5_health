import streamlit as st  # type: ignore
from sample_data import go_to


# --------------------------
# AUTH ENTRY PAGE (FIXED)
# --------------------------
def auth_entry_page():
    st.markdown("<div class='auth-card'>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1.4, 1, 0.9]) 
    
    with col_c:
        logo_container = st.container()
        title_container = st.container()
        subtitle_container = st.container()

        with logo_container:
            try:
                st.image("logo.png", width=140)
            except:
                pass

        with title_container:
            st.markdown("", unsafe_allow_html=True)  # move DOWN
            st.markdown(
                 "<div class='header-title'>HEALTHCARE APP</div>",
                  unsafe_allow_html=True
            )

    colu_l, colu2_c, colu3_r = st.columns([1.5, 1, 0.9]) 

    with colu2_c:
            st.markdown(
                "<div class='subtle'>Secure HealthCare System</div>",
                unsafe_allow_html=True
            )

    col1_l, col2_c, col3_r = st.columns([1.6, 1.2, 1]) 
   
    with col2_c:
        st.markdown('<div class="auth-buttons">', unsafe_allow_html=True)

        if st.button(" Login", key="auth_login_v2"):
            go_to("login")
 
        if st.button(" Sign Up", key="auth_signup_v2"):
            go_to("signup")

    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------
# LOGIN PAGE
# --------------------------
def login_page():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Login")

    _, center, _ = st.columns([1, 2, 1])

    with center:
        st.markdown("<div class='center-label'>Email</div>", unsafe_allow_html=True)
        email = st.text_input("", key="login_email")

        st.markdown("<div class='center-label'>Password</div>", unsafe_allow_html=True)
        password = st.text_input("", type="password", key="login_password")

        b1_left, _, b2_right = st.columns([1, 1, 1])
    
        with b1_left:
            # Changed key for back button on login page
            if st.button("← Back", key="login_back_to_auth"):
                go_to("auth")

        with b2_right:
            if st.button("Login"):
                users = st.session_state.users
                if email in users and users[email]["password"] == password:
                    st.session_state.current_user = email
                    st.session_state.page = "dashboard"
                    st.rerun() 
                else:
                    st.error("Incorrect email or password.")

    st.markdown("</div>", unsafe_allow_html=True)  # Fixed indentation: This closes the card div, so it must be outside the 'with center' block

# --------------------------
# SIGNUP PAGE
# --------------------------
def signup_page():
    st.markdown("### Create Account")

    _, center, _ = st.columns([1, 2, 1])

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

        btn_left, _, btn_right = st.columns([1, 1, 1])

        with btn_left:
            if st.button("← Back", key="signup_back_to_auth"):
                go_to("auth")

        with btn_right:
            if st.button("Sign Up"):

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
    
    st.markdown("</div>", unsafe_allow_html=True)  # Fixed indentation: This closes the card div, so it must be outside the 'with center' block

