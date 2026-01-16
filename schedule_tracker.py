#schedule_tracker.py
import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import heapq
from datetime import datetime
from sample_data import go_to, _parse_time
from medication_tracker import top_nav_bar


def schedule_tracker_page():
    """
    Centralized Schedule Tracker with notifications for medications, vitals, and follow-ups.
    Uses Data Structures: Priority Queue (heap), Queue (FIFO), Stack (LIFO)
    """
    top_nav_bar("Schedule Tracker")
    st.write("")

    patients = st.session_state.get("patients", [])
    if not patients:
        st.info("No patients available. Add a patient first.")
        return

    # Patient selection
    patient_map = {p['name']: p for p in patients}
    selected_key = st.selectbox("Select Patient", list(patient_map.keys()))
    patient = patient_map[selected_key]

    st.markdown(f"<b>{patient['name']}</b> | Age: {patient.get('age', 'N/A')}", unsafe_allow_html=True)
    st.write("---")

    # Display scheduled appointments
    if patient.get("schedules"):
        st.write("### Scheduled Appointments")
        st.dataframe(pd.DataFrame(patient["schedules"]), use_container_width=True)
        st.write("---")

    # Initialize data structures
    schedule_heap = []
    notifications = []
    admin_alerts = []
    now = datetime.now()

    # Build priority queue from medications and vitals
    for med in patient.get("medications", []):
        for t in med.get("times", []):
            dt = _parse_time(t)
            if dt:
                heapq.heappush(schedule_heap, ((dt - now).total_seconds(), dt, "Medication", med["name"]))

    for reading in patient.get("readings", [])[-3:]:
        dt = _parse_time(reading.get("time", ""))
        if dt:
            heapq.heappush(schedule_heap, ((dt - now).total_seconds(), dt, "Vitals Check", "Vitals Review"))

    # Process schedules into upcoming and missed
    upcoming = []
    missed = []
    
    while schedule_heap:
        secs, dt, s_type, label = heapq.heappop(schedule_heap)
        time_str = dt.strftime("%Y-%m-%d %H:%M")
        
        if secs < 0:
            missed.append({"Type": s_type, "Task": label, "Time": time_str})
            notifications.append({"type": "missed", "msg": f"{label} ({s_type}) missed at {dt.strftime('%H:%M')}"})
            admin_alerts.append(f"⚠️ Missed {s_type}: {label} at {dt.strftime('%H:%M')}")
        else:
            upcoming.append({"Type": s_type, "Task": label, "Time": time_str, "Minutes Left": int(secs // 60)})
            if secs < 3600:
                notifications.append({"type": "upcoming", "msg": f"{label} ({s_type}) due in {int(secs//60)} min"})

    # Emergency checks
    emergency_alerts = []
    if patient.get("readings"):
        latest = patient["readings"][-1]
        if latest.get("hr", 0) > 100:
            emergency_alerts.append("🚨 High Heart Rate Detected")
            admin_alerts.append(f"🚨 High Heart Rate: {latest['hr']} bpm")
        if latest.get("temp", 0) > 38:
            emergency_alerts.append("🚨 High Temperature Alert")
            admin_alerts.append(f"🚨 High Temperature: {latest['temp']} °C")

    # Display emergency alerts
    st.write("### Emergency Alerts")
    if emergency_alerts:
        for alert in emergency_alerts:
            st.error(alert)
    else:
        st.success("✅ No emergency alerts.")

    # Display notifications
    st.write("### Notifications")
    if notifications:
        for n in notifications:
            if n["type"] == "missed":
                st.warning(n["msg"])
            else:
                st.info(n["msg"])
    else:
        st.success("✅ No new notifications.")

    # Display upcoming schedules
    st.write("### Upcoming Schedules")
    if upcoming:
        st.dataframe(pd.DataFrame(upcoming), use_container_width=True)
    else:
        st.info("No upcoming schedules.")

    # Display missed schedules
    st.write("### Missed Schedules")
    if missed:
        st.dataframe(pd.DataFrame(missed), use_container_width=True)
    else:
        st.success("✅ No missed schedules.")

    # Display admin alerts
    st.write("### Admin Alerts")
    if admin_alerts:
        for alert in admin_alerts:
            st.error(alert)
    else:
        st.success("✅ All patients are stable.")
