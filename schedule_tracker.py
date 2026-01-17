# schedule_tracker.py
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import heapq
from datetime import datetime
from sample_data import go_to, _parse_time
from medication_tracker import top_nav_bar

def schedule_tracker_page():
    """
    Centralized Schedule Tracker with:
    - Time-based medication alerts
    - Missed vitals alerts (pending in red, taken ✅)
    - Dismiss feature for medication alerts
    """
    top_nav_bar("Schedule Tracker")
    st.write("")

    # ---------------- SESSION STATE ----------------
    if "dismissed_meds" not in st.session_state:
        st.session_state["dismissed_meds"] = set()
    if "data_updated" not in st.session_state:
        st.session_state["data_updated"] = "init"
    if "missed_vitals" not in st.session_state:
        st.session_state["missed_vitals"] = []

    # ---------------- PATIENT DATA ----------------
    patients = st.session_state.get("patients", [])
    if not patients:
        st.info("No patients available. Add a patient first.")
        return

    # ---------------- PATIENT SELECTION ----------------
    patient_map = {p["name"]: p for p in patients}
    selected_key = st.selectbox("Select Patient", list(patient_map.keys()))
    patient = patient_map[selected_key]

    st.markdown(
        f"<b>{patient['name']}</b> | Age: {patient.get('age', 'N/A')}",
        unsafe_allow_html=True
    )
    st.write("---")

    now = datetime.now()

    # ---------------- TIME-BASED MISSED MEDICATION ALERT ----------------
    st.write("### 🚨 Missed Medication Alerts")
    missed_meds = []

    for med in patient.get("medications", []):
        for t in med.get("times", []):
            scheduled_time = _parse_time(t)
            if not scheduled_time:
                continue

            if now > scheduled_time:
                last_taken = med.get("last_taken")
                was_taken = False
                if last_taken:
                    try:
                        last_taken_dt = datetime.strptime(last_taken, "%Y-%m-%d %H:%M")
                        if last_taken_dt >= scheduled_time:
                            was_taken = True
                    except:
                        pass

                alert_id = f"{patient['name']}_{med['name']}_{scheduled_time}"

                if not was_taken and alert_id not in st.session_state["dismissed_meds"]:
                    missed_meds.append({
                        "id": alert_id,
                        "Patient": patient["name"],
                        "Medication": med["name"],
                        "Dose": med.get("dose", ""),
                        "Scheduled Time": scheduled_time.strftime("%H:%M"),
                        "Minutes Late": int((now - scheduled_time).total_seconds() // 60)
                    })

    if missed_meds:
        for m in missed_meds:
            with st.container():
                st.error(
                    f"🚑 **Patient:** {m['Patient']}\n"
                    f"💊 **Medication:** {m['Medication']} {m['Dose']}\n"
                    f"⏰ **Missed at:** {m['Scheduled Time']}\n"
                    f"⏳ **Late by:** {m['Minutes Late']} minutes"
                )
                if st.button("Dismiss Alert", key=m["id"]):
                    st.session_state["dismissed_meds"].add(m["id"])
                    st.rerun()
    else:
        st.success("✅ No missed medications at this time.")

    st.write("---")

    # ---------------- SCHEDULE OVERVIEW ----------------
    schedule_heap = []
    upcoming = []
    missed = []
    admin_alerts = []

    # Medications
    for med in patient.get("medications", []):
        for t in med.get("times", []):
            dt = _parse_time(t)
            if dt:
                heapq.heappush(
                    schedule_heap,
                    ((dt - now).total_seconds(), dt, "Medication", med["name"])
                )

    # Latest readings
    for reading in patient.get("readings", [])[-3:]:
        dt = _parse_time(reading.get("time", ""))
        if dt:
            heapq.heappush(
                schedule_heap,
                ((dt - now).total_seconds(), dt, "Vitals Check", "Vitals Review")
            )

    # Process heap
    while schedule_heap:
        secs, dt, s_type, label = heapq.heappop(schedule_heap)
        time_str = dt.strftime("%Y-%m-%d %H:%M")

        if secs < 0:
            missed.append({
                "Type": s_type,
                "Task": label,
                "Time": time_str
            })
            admin_alerts.append(f" Missed {s_type}: {label} at {dt.strftime('%H:%M')}")
        else:
            upcoming.append({
                "Type": s_type,
                "Task": label,
                "Time": time_str,
                "Minutes Left": int(secs // 60)
            })

    # ---------------- EMERGENCY CHECKS ----------------
    emergency_alerts = []
    if patient.get("readings"):
        latest = patient["readings"][-1]
        if latest.get("hr", 0) > 100:
            emergency_alerts.append(" High Heart Rate Detected")
            admin_alerts.append(f" High Heart Rate: {latest['hr']} bpm")
        if latest.get("temp", 0) > 38:
            emergency_alerts.append(" High Temperature Alert")
            admin_alerts.append(f" High Temperature: {latest['temp']} °C")

    # ---------------- DISPLAY SECTIONS ----------------
    st.write("### Emergency Alerts")
    if emergency_alerts:
        for alert in emergency_alerts:
            st.error(alert)
    else:
        st.success("✅ No emergency alerts.")

    st.write("### Upcoming Schedules")
    if upcoming:
        st.dataframe(pd.DataFrame(upcoming), use_container_width=True)
    else:
        st.info("No upcoming schedules.")

    # ----------------- MISSED VITALS (Latest per vital, selected patient only) -----------------
    st.write("### Missed Vitals")

    patient_vitals = patient.get("vitals", [])
    if not patient_vitals:
        st.success("✅ No vitals recorded for this patient.")
    else:
        # Keep only the latest record per vital
        latest_vitals = {}
        for v in patient_vitals:
            name = v["name"]
            time_str = v.get("time", "1970-01-01 00:00")
            if name not in latest_vitals or time_str > latest_vitals[name].get("time", "1970-01-01 00:00"):
                latest_vitals[name] = v

        for v_name, vital in latest_vitals.items():
            status = vital.get("status", "Pending")
            time = vital.get("time", "N/A")
            hr = latest_vitals.get("Heart Rate", {}).get("value", "N/A")
            bp = latest_vitals.get("Blood Pressure", {}).get("value", "N/A")
            temp = latest_vitals.get("Temperature", {}).get("value", "N/A")

            if status == "Taken":
                st.success(
                    f"Patient: {patient['name']}\n"
                    f"Vital: {v_name} ✅ Last Recorded: {time}\n"
                    f"HR: {hr} bpm | BP: {bp} | Temp: {temp}"
                )
            else:
                st.error(
                    f"Patient: {patient['name']}\n"
                    f"Vital: {v_name} (Pending) Scheduled at: {time}\n"
                    f"HR: {hr} bpm | BP: {bp} | Temp: {temp}"
                )

    # ----------------- ADMIN ALERTS SUMMARY -----------------
    st.write("### Admin Alerts Summary")
    if admin_alerts:
        for alert in admin_alerts:
            st.error(alert)
    else:
        st.success("✅ All patients are stable.")
