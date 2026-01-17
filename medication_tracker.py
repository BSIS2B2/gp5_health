import streamlit as st  # type: ignore
from datetime import datetime
from sample_data import go_to

# ----------------------------------------
# DATA SYNC HELPER
# ----------------------------------------
def sync_patients(patients):
    st.session_state["patients"] = patients
    st.session_state["data_updated"] = datetime.now().isoformat()

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

    meds = patient.setdefault("medications", [])

    # ----------------------------------------
    # ADD MEDICATION SECTION
    # ----------------------------------------
    with st.expander("➕ Add New Medication"):
        with st.form("add_med_form"):
            new_name = st.text_input("Medication Name")
            new_dose = st.text_input("Dosage (e.g. 500mg)")
            new_times = st.text_input("Times (comma separated, e.g. 08:00, 20:00)")
            submit = st.form_submit_button("Save Medication")

            if submit:
                if new_name and new_dose:
                    meds.append({
                        "name": new_name,
                        "dose": new_dose,
                        "times": [t.strip() for t in new_times.split(",")],
                        "last_taken": None
                    })
                    sync_patients(patients)
                    st.success(f"Added {new_name}")
                    st.rerun()
                else:
                    st.error("Please fill in Name and Dosage")

    # ----------------------------------------
    # MEDICATION LIST
    # ----------------------------------------
    st.subheader("Medication List")
    h1, h2, h3, h4, h5 = st.columns([2, 1.2, 1.5, 1.5, 2.5])
    h1.write("**Name**")
    h2.write("**Dose**")
    h3.write("**Times**")
    h4.write("**Last Taken**")
    h5.write("**Actions**")

    for idx, med in enumerate(meds):
        with st.container():
            c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1.5, 1.5, 2.5])

            c1.markdown(f"**{med['name']}**")
            c2.write(med["dose"])
            c3.write(", ".join(med["times"]))
            c4.write(med.get("last_taken") or "—")

            current_status = "Taken" if med.get("last_taken") else "Pending"
            status = c5.radio(
                f"Status for {med['name']}",
                ["Pending", "Taken"],
                index=0 if current_status == "Pending" else 1,
                key=f"status_{selected}_{idx}",
                horizontal=True,
                label_visibility="collapsed"
            )

            if status == "Taken" and not med.get("last_taken"):
                med["last_taken"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                sync_patients(patients)
                st.rerun()

            if status == "Pending" and med.get("last_taken"):
                med["last_taken"] = None
                sync_patients(patients)
                st.rerun()

            btn_col1, btn_col2 = c5.columns(2)

            if btn_col1.button("📝 Edit", key=f"edit_{idx}"):
                st.session_state[f"editing_{idx}"] = True

            if btn_col2.button("🗑️ Delete", key=f"del_{idx}"):
                meds.pop(idx)
                sync_patients(patients)
                st.warning(f"Deleted {med['name']}")
                st.rerun()

            if st.session_state.get(f"editing_{idx}"):
                with st.form(f"edit_form_{idx}"):
                    edit_name = st.text_input("Name", med['name'])
                    edit_dose = st.text_input("Dose", med['dose'])
                    edit_times = st.text_input("Times", ", ".join(med['times']))
                    if st.form_submit_button("Update"):
                        med['name'] = edit_name
                        med['dose'] = edit_dose
                        med['times'] = [t.strip() for t in edit_times.split(",")]
                        del st.session_state[f"editing_{idx}"]
                        sync_patients(patients)
                        st.rerun()

            st.divider()

    # ----------------------------------------
    # VITALS TRACKER SECTION
    # ----------------------------------------
    st.subheader("Vitals Tracker")
    vitals = patient.setdefault("vitals", [])

    # Ensure all default vitals exist
    default_vitals = ["Heart Rate", "Blood Pressure", "Temperature"]
    for dv in default_vitals:
        if not any(v["name"] == dv for v in vitals):
            vitals.append({
                "name": dv,
                "status": "Pending",
                "value": None,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
    sync_patients(patients)

    # Display vitals
    for idx, vital in enumerate(vitals):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{vital['name']}** — Last Recorded: {vital.get('time', 'N/A')}")

        with c2:
            status = st.radio(
                "",
                ["Pending", "Taken"],
                index=0 if vital["status"] == "Pending" else 1,
                key=f"vital_status_{selected}_{idx}",
                horizontal=True,
                label_visibility="collapsed"
            )

            if status != vital["status"]:
                vital["status"] = status
                vital["time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                sync_patients(patients)

            if status == "Taken":
                if vital["name"] == "Heart Rate":
                    vital["value"] = st.number_input(
                        "Enter BPM",
                        min_value=0,
                        max_value=300,
                        value=vital.get("value") or 70,
                        key=f"{vital['name']}_input_{selected}_{idx}"
                    )
                elif vital["name"] == "Blood Pressure":
                    vital["value"] = st.text_input(
                        "Enter BP (e.g., 120/80)",
                        value=vital.get("value") or "",
                        key=f"{vital['name']}_input_{selected}_{idx}"
                    )
                elif vital["name"] == "Temperature":
                    vital["value"] = st.number_input(
                        "Enter Temperature (°C)",
                        min_value=30.0,
                        max_value=45.0,
                        value=vital.get("value"),
                        format="%.1f",
                        key=f"{vital['name']}_input_{selected}_{idx}"
                    )
                sync_patients(patients)

    st.markdown(f"""
        <div style="background:#fff;padding:16px;border-radius:12px;
        box-shadow:0 6px 18px rgba(0,0,0,.06);margin-top:16px">
        <b>{patient['name']}</b> — Age: {patient.get('age','N/A')}
        </div>
    """, unsafe_allow_html=True)
