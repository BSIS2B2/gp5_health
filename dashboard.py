# dashboard.py
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import altair as alt  # type: ignore
from datetime import datetime
from random import choice
from medication_tracker import top_nav_bar

# ----------------------------------------
# HELPERS
# ----------------------------------------
@st.cache_data(ttl=10)
def process_patient_readings(patients_data, data_updated):
    # data_updated ensures cache invalidation when medication is updated
    records = []
    for p in patients_data:
        readings = p.get("readings", [])
        if readings:
            latest = readings[-1]  # latest reading only
            records.append({
                "patient": p.get("name", "N/A"),
                "time": datetime.strptime(
                    latest.get("time", "2026-01-01 00:00"),
                    "%Y-%m-%d %H:%M"
                ),
                "Heart Rate": latest.get("hr", 0),
                "BP Systolic": latest.get("bp_sys", 0),
                "BP Diastolic": latest.get("bp_dia", 0),
                "Temperature": latest.get("temp", 0)
            })
    return records

def _initialize_sample_patients():
    genders = ["Male", "Female", "Other"]
    patients = []
    for i in range(1, 21):  # PT 001 → PT 020
        patients.append({
            "name": f"PT {i:03d}",
            "age": 20 + i,
            "gender": choice(genders),
            "readings": [
                {
                    "time": "2026-01-16 08:00",
                    "hr": 60 + i,
                    "bp_sys": 110 + i,
                    "bp_dia": 70 + i // 2,
                    "temp": 98.6
                }
            ],
            "medications": [],
            "schedules": []
        })
    return patients

# ----------------------------------------
# CRUD PAGES
# ----------------------------------------
def _create_patient():
    st.subheader(" Add Patient")
    with st.form("create_patient"):
        name = st.text_input("Name")
        age = st.number_input("Age", 1, 120, 25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])

        st.markdown("###  Initial Vitals (Optional)")

        # ---------------------------
        # DATETIME INPUT FOR VITALS
        # ---------------------------
        vitals_time = st.datetime_input(
            "Record Time (Optional)", 
            value=datetime.now(),
            help="Set the date and time for these vitals"
        )

        hr = st.number_input("Heart Rate (bpm)", 30, 200)
        bp_sys = st.number_input("BP Systolic (mmHg)", 80, 200)
        bp_dia = st.number_input("BP Diastolic (mmHg)", 40, 150)
        temp = st.number_input("Temperature (°C)", 30.0, 45.0, step=0.1)

        col1, col2 = st.columns([1.5, 0.1])
        with col1:
            submit = st.form_submit_button("Create")
        with col2:
            cancel = st.form_submit_button("Cancel", type="secondary")

        if submit:
            if not name.strip():
                st.error("Name required")
                return

            new_patient = {
                "name": name,
                "age": age,
                "gender": gender,
                "readings": [],
                "medications": [],
                "schedules": []
            }

            # ---------------------------
            # APPEND INITIAL VITALS
            # ---------------------------
            if hr or bp_sys or bp_dia or temp:
                new_patient["readings"].append({
                    "time": vitals_time.strftime("%Y-%m-%d %H:%M"),
                    "hr": hr,
                    "bp_sys": bp_sys,
                    "bp_dia": bp_dia,
                    "temp": temp
                })

            st.session_state.patients.append(new_patient)
            st.session_state.data_updated = datetime.now().isoformat()  # sync fix

            st.session_state.selected_patient = name
            st.session_state.crud_action = "read"
            st.success(f"Patient {name} added ✅")
            st.rerun()

        if cancel:
            st.info("Patient creation cancelled")
            st.session_state.crud_action = None
            st.rerun()

def _read_patient():
    st.subheader(" View Patient")
    patients = st.session_state.get("patients", [])
    if not patients:
        st.info("No patients available.")
        return

    names = [p.get("name", "N/A") for p in patients]
    selected = st.selectbox("Select Patient", names)

    st.session_state.selected_patient = selected
    patient = next((p for p in patients if p.get("name") == selected), {})

    # ---------- BASIC INFO ----------
    st.markdown("###  Patient Info")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {patient.get('name', 'N/A')}")
        st.write(f"**Age:** {patient.get('age', 'N/A')}")
    with col2:
        st.write(f"**Gender:** {patient.get('gender', 'N/A')}")

    # ---------- MEDICATIONS ----------
    st.divider()
    st.markdown("### Medications")
    meds = patient.get("medications", [])
    if meds:
        meds_rows = []
        for m in meds:
            meds_rows.append({
                "Name": m.get("name", "N/A"),
                "Dose": m.get("dose", "N/A"),
                "Times": ", ".join(m.get("times", [])),
                "Last Taken": m.get("last_taken") or "Not yet"
            })
        st.dataframe(pd.DataFrame(meds_rows), use_container_width=True)
    else:
        st.info("No medications recorded.")

    # ---------- VITAL READINGS ----------
    st.divider()
    st.markdown("###  Vital Readings")
    readings = patient.get("readings", [])
    if readings:
        vitals_df = pd.DataFrame(readings)
        vitals_df["time"] = pd.to_datetime(vitals_df.get("time", "2026-01-01 00:00"))
        vitals_df = vitals_df.sort_values("time", ascending=False)
        vitals_df.rename(columns={
            "hr": "Heart Rate",
            "bp_sys": "BP Systolic",
            "bp_dia": "BP Diastolic",
            "temp": "Temperature (°C)",
            "time": "Recorded At"
        }, inplace=True)
        st.dataframe(vitals_df, use_container_width=True)

        st.subheader("Heart Rate Trend")
        chart = alt.Chart(vitals_df).mark_line(point=True).encode(
            x="Recorded At:T",
            y="Heart Rate:Q"
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No vital readings available.")

def _update_patient():
    st.subheader(" Edit Patient")
    names = [p.get("name", "N/A") for p in st.session_state.get("patients", [])]
    selected = st.selectbox("Select Patient", names)
    patient = next((p for p in st.session_state.patients if p.get("name") == selected), {})

    latest_vitals = patient.get("readings", [])
    latest_vitals = latest_vitals[-1] if latest_vitals else {"hr": 70, "bp_sys": 120, "bp_dia": 80, "temp": 37.0}

    with st.form("edit_patient"):
        patient["name"] = st.text_input("Name", patient.get("name", ""))
        patient["age"] = st.number_input("Age", 1, 120, patient.get("age", 25))
        patient["gender"] = st.selectbox(
            "Gender", ["Male", "Female", "Other"],
            index=["Male", "Female", "Other"].index(patient.get("gender", "Male"))
        )

        st.markdown("### 🩺 Update Vitals (Optional)")
        hr = st.number_input("Heart Rate (bpm)", 30, 200, value=latest_vitals.get("hr", 70))
        bp_sys = st.number_input("BP Systolic (mmHg)", 80, 200, value=latest_vitals.get("bp_sys", 120))
        bp_dia = st.number_input("BP Diastolic (mmHg)", 40, 150, value=latest_vitals.get("bp_dia", 80))
        temp = st.number_input("Temperature (°C)", 30.0, 45.0, step=0.1, value=latest_vitals.get("temp", 37.0))

        col1, col2 = st.columns([1., 0.1])
        with col1:
            update_btn = st.form_submit_button("Update")
        with col2:
            cancel_btn = st.form_submit_button("Cancel")

        if update_btn:
            patient["readings"].append({
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "hr": hr,
                "bp_sys": bp_sys,
                "bp_dia": bp_dia,
                "temp": temp
            })
            st.session_state.data_updated = datetime.now().isoformat()  # sync fix
            st.success("Patient updated with new vitals ✅")
            st.rerun()

        if cancel_btn:
            st.info("Edit cancelled")
            st.session_state.crud_action = None
            st.rerun()

def _delete_patient():
    st.subheader(" Delete Patient")
    names = [p.get("name", "N/A") for p in st.session_state.get("patients", [])]
    selected = st.selectbox("Select Patient", names)

    if st.button("Confirm Delete"):
        st.session_state.patients = [
            p for p in st.session_state.patients if p.get("name") != selected
        ]
        st.session_state.data_updated = datetime.now().isoformat()  # sync fix
        st.success("Deleted")
        st.rerun()

# ----------------------------------------
# DASHBOARD PAGE
# ----------------------------------------
def dashboard():
    if "patients" not in st.session_state:
        st.session_state.patients = _initialize_sample_patients()
    if "crud_action" not in st.session_state:
        st.session_state.crud_action = None
    if "selected_patient" not in st.session_state:
        st.session_state.selected_patient = None
    if "data_updated" not in st.session_state:
        st.session_state.data_updated = "init"

    top_nav_bar("Health Metric Dashboard")
    st.divider()

    _, right = st.columns([7, 3])
    with right:
        b1, b2, b3, b4 = st.columns([1, 1, 1, 1])
        with b1:
            if st.button("✚", help="Add Patient", key="btn_add"):
                st.session_state.crud_action = "create"
        with b2:
            if st.button("👁️‍🗨️", help="View Patient", key="btn_view"):
                st.session_state.crud_action = "read"
        with b3:
            if st.button("✎", help="Edit Patient", key="btn_edit"):
                st.session_state.crud_action = "update"
        with b4:
            if st.button("⌫", help="Delete Patient", key="btn_delete"):
                st.session_state.crud_action = "delete"

    st.divider()

    action = st.session_state.crud_action
    if action == "create":
        _create_patient()
    elif action == "read":
        _read_patient()
    elif action == "update":
        _update_patient()
    elif action == "delete":
        _delete_patient()

    if action not in ["update", "read", "create"]:
        patients = st.session_state.patients[:20]
        records = process_patient_readings(
            tuple(patients),
            st.session_state.data_updated
        )
        df = pd.DataFrame(records)

        if not df.empty:
            st.subheader("Vitals Table")
            st.dataframe(df.sort_values("time", ascending=False), use_container_width=True)

            st.subheader("Heart Rate Trend")
            chart = alt.Chart(df).mark_line(point=True).encode(
                x="time:T",
                y="Heart Rate:Q",
                color="patient:N"
            )
            st.altair_chart(chart, use_container_width=True)
