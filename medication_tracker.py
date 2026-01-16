import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
from datetime import datetime
from sample_data import go_to

# ----------------------------------------
# NAVIGATION BAR
# ----------------------------------------
def top_nav_bar(title=""):
    cols = st.columns([3, 1, 1, 1, 1, 1])
    with cols[0]:
        st.markdown(
            f"<div style='font-size:20px; color:#0b5394; font-weight:700'>{title}</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='muted'>Signed in as: <b>{st.session_state.current_user}</b></div>",
            unsafe_allow_html=True
        )

    nav_buttons = [
        ("Dashboard", "dashboard"),
        ("Medication", "medication"),
        ("Profile", "user_info"),
        ("Schedule Tracker", "schedule"),
    ]

    for i, (label, page) in enumerate(nav_buttons, 1):
        with cols[i]:
            if st.button(label):
                go_to(page)
                st.rerun()

    with cols[5]:
        if st.button("Logout"):
            st.session_state.current_user = None
            go_to("auth")
            st.rerun()

# ----------------------------------------
# MEDICATION PAGE
# ----------------------------------------
def medication_page():

    top_nav_bar("Medication Reminder & Tracker")
    st.divider()

    patients = st.session_state.get("patients", [])
    if not patients:
        st.info("No patients available.")
        return

    patient_names = [p["name"] for p in patients]
    selected = st.selectbox("Select Patient", patient_names)
    patient = next(p for p in patients if p["name"] == selected)

    meds = patient.get("medications", [])

    if not meds:
        st.info("No medications yet.")
        return

    st.subheader("Medication List")

    for idx, med in enumerate(meds):
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1.5, 1.5, 2])

            c1.markdown(f"**{med['name']}**")
            c2.write(med["dose"])
            c3.write(", ".join(med["times"]))
            c4.write(med.get("last_taken") or "—")

            # -----------------------------
            # STATUS RADIO (NO SEARCH BAR)
            # -----------------------------
            current_status = "Taken" if med.get("last_taken") else "Pending"

            status = c5.radio(
                "Status",
                ["Pending", "Taken"],
                index=0 if current_status == "Pending" else 1,
                key=f"status_{selected}_{idx}",
                horizontal=True
            )

            # UPDATE STATUS
            if status == "Taken" and not med.get("last_taken"):
                med["last_taken"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.success(f"{med['name']} marked as Taken")
                st.rerun()

            if status == "Pending" and med.get("last_taken"):
                med["last_taken"] = None
                st.info(f"{med['name']} marked as Pending")
                st.rerun()

            st.divider()

    # ---------- PATIENT INFO ----------
    st.markdown(f"""
        <div style="background:#fff;padding:16px;border-radius:12px;
        box-shadow:0 6px 18px rgba(0,0,0,.06);margin-top:16px">
        <b>{patient['name']}</b> — Age: {patient.get('age','N/A')}
        </div>
    """, unsafe_allow_html=True)
