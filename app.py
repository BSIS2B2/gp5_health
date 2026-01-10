import streamlit as st  # type: ignore

from sample_data import generate_sample_patients, is_authenticated
from auth import auth_entry_page, login_page, signup_page
from dashboard import dashboard
from medication_tracker import medication_page
from schedtracker import schedule_tracker_page
from user_info import user_info_page


# --------------------------
# PAGE CONFIG
# --------------------------
st.set_page_config(
    page_title="Healthcare DSA App",
    page_icon="⚕️",
    layout="wide"
)


# --------------------------
# LOAD CSS (SEPARATED)
# --------------------------
def load_css(file_name: str):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles.css")


# --------------------------
# SESSION STATE INIT
# --------------------------
def init_session_state():
    defaults = {
        "page": "auth",
        "users": {},
        "current_user": None,
        "patients": generate_sample_patients(25)
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# --------------------------
# SAFE NAVIGATION
# --------------------------
def go_to_page(page_name: str):
    st.session_state.page = page_name
    st.rerun()


# --------------------------
# ROUTER
# --------------------------
def run_app():
    page = st.session_state.page

    # ----- PUBLIC PAGES -----
    public_pages = {
        "auth": auth_entry_page,
        "login": login_page,
        "signup": signup_page
    }

    if page in public_pages:
        public_pages[page]()
        return

    # ----- AUTH CHECK -----
    if not is_authenticated():
        st.warning("You must log in to access that page.")
        if st.button("Go to Login"):
            go_to_page("login")
        return

    # ----- PROTECTED PAGES -----
    protected_pages = {
        "dashboard": dashboard,
        "medication": medication_page,
        "schedule": schedule_tracker_page,
        "user_info": user_info_page
    }

    protected_pages.get(page, dashboard)()


# --------------------------
# RUN APP
# --------------------------
run_app()