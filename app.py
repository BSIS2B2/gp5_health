import streamlit as st  # type: ignore
from sample_data import generate_sample_patients, is_authenticated, go_to
from auth import auth_entry_page, login_page, signup_page
from dashboard import dashboard_page
from medication_tracker import medication_page
from user_info import user_info_page

st.set_page_config(
    page_title="Healthcare DSA App",
    page_icon="⚕️",
    layout="wide"
)

# --------------------------
# CSS / STYLING
# --------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: #f6fbff;
        font-family: 'Inter', sans-serif;
    }

    .auth-card {
        background: white;
        margin: 60px auto;
        padding: 28px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(11,83,148,0.08);
        text-align: center;
    }

    .card {
        background: white;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 6px 18px rgba(11,83,148,0.06);
    }

    .header-title {
        color: #0b5394;
        font-weight: 700;
        font-size: 22px;
        margin-bottom: 4px;
    }

    .subtle {
        color: #666;
        font-size: 13px;
        margin-bottom: 16px;
    }

    /* Center labels */
    .center-label {
        text-align: left;
        font-weight: 600;
        color: black;
        margin-top: 8px;
        font-size: 14px;
    }

    /* Force wider text fields by targeting the container and using !important */
    div[data-testid="stTextInput"] > div,
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stSelectbox"] > div {
        width: 50% !important; 
        margin: 0 !important;
    }


    div[data-testid="baseInput-container"] input[type="password"] + div,
    div[data-testid="baseInput-container"] input[type="text"] + div {
        margin-right: 0 !important; 
        margin-left: auto !important; 
        padding-right: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# SESSION STATE
# --------------------------
if "page" not in st.session_state:
    st.session_state.page = "auth"

if "users" not in st.session_state:
    st.session_state.users = {}

if "current_user" not in st.session_state:
    st.session_state.current_user = None

if "patients" not in st.session_state:
    st.session_state.patients = generate_sample_patients(25)

# --------------------------
# ROUTER
# --------------------------
def run_app():
    page = st.session_state.page

    if page == "auth":
        auth_entry_page()
    elif page == "login":
        login_page()
    elif page == "signup":
        signup_page()
    else:
        if not is_authenticated():
            st.warning("You must log in to access that page.")
            if st.button("Go to Login"):
                go_to("login")
            return

        if page == "dashboard":
            dashboard_page()
        elif page == "medication":
            medication_page()
        elif page == "user_info":
            user_info_page()
        else:
            go_to("dashboard")

run_app()