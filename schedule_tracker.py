import streamlit as st  # type: ignore
import pandas as pd     # type: ignore
import heapq
from datetime import datetime
from sample_data import go_to, _parse_time
from medication_tracker import top_nav_bar


# ----------------------------------------
# SCHEDULE TRACKER PAGE WITH NOTIFICATIONS
# ----------------------------------------
def schedule_tracker_page():
    """
    Centralized Schedule Tracker with notifications for:
    - Medications
    - Vitals
    - Follow-ups

    Uses DSA:
    - Priority Queue (heap)
    - Queue (FIFO)
    - Stack (LIFO)
    """
    top_nav_bar("Schedule Tracker")
    st.write("")

    patients = st.session_state.patients

    # -----------------------------
    # PATIENT SELECTION (HASH MAP)
    # -----------------------------
    patient_map = {f"{p['id']} — {p['name']}": p for p in patients}
    selected_key = st.selectbox("Select Patient", list(patient_map.keys()))
    patient = patient_map[selected_key]

    st.markdown(f"<b>{patient['name']}</b> | Age: {patient['age']}</div>", unsafe_allow_html=True)
    st.write("---")

    # -----------------------------
    # BUILD SCHEDULE HEAP
    # -----------------------------
    schedule_heap = []        # Priority Queue
    missed_queue = []         # Queue
    emergency_stack = []      # Stack
    notifications = []        # Notifications for UI

    now = datetime.now()

    # ---- MEDICATION SCHEDULES
    for med in patient["medications"]:
        for t in med["times"]:
            dt = _parse_time(t)
            if not dt:
                continue
            diff = (dt - now).total_seconds()
            heapq.heappush(schedule_heap, (diff, dt, "Medication", med["name"]))

    # ---- VITAL CHECK SCHEDULES
    for reading in patient["readings"][-3:]:
        dt = _parse_time(reading["time"])
        if not dt:
            continue
        heapq.heappush(schedule_heap, ((dt-now).total_seconds(), dt, "Vitals Check", "Vitals Review"))

    # -----------------------------
    # PROCESS SCHEDULES
    # -----------------------------
    upcoming = []
    while schedule_heap:
        secs, dt, s_type, label = heapq.heappop(schedule_heap)
        if secs < 0:
            missed_queue.append({
                "Type": s_type,
                "Task": label,
                "Time": dt.strftime("%Y-%m-%d %H:%M")
            })
            notifications.append({
                "type": "missed",
                "msg": f" {label} ({s_type}) missed at {dt.strftime('%H:%M')}"
            })
        else:
            upcoming.append({
                "Type": s_type,
                "Task": label,
                "Time": dt.strftime("%Y-%m-%d %H:%M"),
                "Minutes Left": int(secs // 60)
            })
            if secs < 3600:  # less than 1 hour
                notifications.append({
                    "type": "upcoming",
                    "msg": f" {label} ({s_type}) due in {int(secs//60)} min"
                })

    # -----------------------------
    # EMERGENCY STACK CHECK
    # -----------------------------
    latest = patient["readings"][-1]
    if latest["hr"] > 100:
        emergency_stack.append("High Heart Rate Detected")
    if latest["temp"] > 38:
        emergency_stack.append("High Temperature Alert")

    # -----------------------------
    # DISPLAY EMERGENCIES (STACK)
    # -----------------------------
    st.write("### Emergency Alerts")
    if emergency_stack:
        while emergency_stack:
            st.error(emergency_stack.pop())
    else:
        st.success("No emergency alerts.")

    # -----------------------------
    # DISPLAY NOTIFICATIONS
    # -----------------------------
    st.write("### Notifications")
    if notifications:
        for n in notifications:
            if n["type"] == "missed":
                st.warning(n["msg"])
            elif n["type"] == "upcoming":
                st.info(n["msg"])
    else:
        st.success("No new notifications.")

    # -----------------------------          
    # DISPLAY UPCOMING (PRIORITY QUEUE)
    # -----------------------------
    st.write("### Upcoming Schedules")
    if upcoming:
        st.dataframe(pd.DataFrame(upcoming), use_container_width=True)
    else:
        st.info("No upcoming schedules.")

    # -----------------------------
    # DISPLAY MISSED (QUEUE)
    # -----------------------------
    st.write("### Missed Schedules")
    if missed_queue:
        st.dataframe(pd.DataFrame(missed_queue), use_container_width=True)
    else:
        st.success("No missed schedules")



