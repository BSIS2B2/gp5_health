# medication_tracker.py (UPDATED)
import streamlit as st # type: ignore
import pandas as pd # type: ignore
import altair as alt # type: ignore
import heapq
import time
from datetime import datetime
from sample_data import go_to, _parse_time

# --- Small top nav for logged-in pages ---
def top_nav_bar(title=""):
    """Displays the navigation bar for logged-in users, now including Profile."""
    # Adjusted columns from 4 to 5 to accommodate the new "Profile" button
    cols = st.columns([3, 1, 1, 1, 1]) 
    with cols[0]:
        st.markdown(f"<div style='font-size:20px; color:#0b5394; font-weight:700'>{title}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='muted'>Signed in as: <b>{st.session_state.current_user}</b></div>", unsafe_allow_html=True)
    with cols[1]:
        if st.button("Dashboard", key="nav_dash"):
            go_to("dashboard")
    with cols[2]:
        if st.button("Medication", key="nav_med"):
            go_to("medication")
    with cols[3]:
        # NEW BUTTON: User Info route
        if st.button("Profile", key="nav_profile"):
            go_to("user_info")
    with cols[4]:
        if st.button("Logout", key="nav_logout"):
            st.session_state.current_user = None
            go_to("auth")

# --- MEDICATION TRACKER PAGE ---
def medication_page():
    """Displays the medication tracking dashboard for a selected patient."""
    top_nav_bar("Medication Reminder & Tracker")
    st.write("")  # spacing
    patients = st.session_state.patients

    # Patient selector and quick stats
    colp1, colp2 = st.columns([2,1])
    with colp1:
        sel = st.selectbox("Select patient", [f"{p['id']} — {p['name']}" for p in patients], index=0)
        patient_index = next(i for i,p in enumerate(patients) if f"{p['id']} — {p['name']}" == sel)
        patient = patients[patient_index]
        st.markdown(f"<div class='card'><b>{patient['name']}</b> — Age: {patient['age']}</div>", unsafe_allow_html=True)
    with colp2:
        total_meds = len(patient['medications'])
        total_readings = len(patient['readings'])
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("**Quick Stats**")
        st.write(f"Med count: {total_meds}")
        st.write(f"Readings: {total_readings}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    # medication table
    med_rows = []
    for m in patient['medications']:
        med_rows.append({
            "Medication": m['name'],
            "Dose": m['dose'],
            "Times": ", ".join(m['times']),
            "Last taken": m['last_taken'] or "-"
        })
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write("### Medication List")
    st.dataframe(pd.DataFrame(med_rows), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Upcoming / Missed doses using priority queue (Min-Heap)
    st.write("### 💊 Upcoming / Missed doses (Priority Queue)")
    pq = []
    now = datetime.now()
    for m in patient['medications']:
        for t in m['times']:
            dt = _parse_time(t)
            if not dt: continue
            # Calculate time difference in seconds for priority
            secs = (dt - now).total_seconds()
            # Push (seconds, datetime, medication name) onto the min-heap
            heapq.heappush(pq, (secs, dt, m['name']))

    notify_html = ""
    shown = 0
    # Pop from the heap to get the most urgent doses first (lowest seconds value)
    while pq and shown < 6:
        secs, dt, med_name = heapq.heappop(pq)
        if secs <= 0:
            notify_html += f"""
            <div class='notify slide-in' style='border-left-color:red;'>
              <div><b>{med_name}</b> — <span class='small'>**Missed** at {dt.strftime('%Y-%m-%d %H:%M')}</span></div>
              <div class='small'>Tap 'Mark as taken' when dose given.</div>
            </div>
            """
        else:
            mins = int(secs//60)
            notify_html += f"""
            <div class='notify slide-in'>
              <div><b>{med_name}</b> — <span class='small'>Due in **{mins} min** at {dt.strftime('%Y-%m-%d %H:%M')}</span></div>
            </div>
            """
        shown += 1

    st.markdown(notify_html, unsafe_allow_html=True)

    # Mark as taken
    st.write("### Mark medication as taken")
    med_names = [m['name'] for m in patient['medications']]
    sel_med = st.selectbox("Medication", med_names, key=f"medsel_{patient_index}")
    if st.button("Mark as taken", key=f"takemed_{patient_index}"):
        for m in patient['medications']:
            if m['name'] == sel_med:
                m['last_taken'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.success(f"{sel_med} marked as taken.")
                st.balloons()
                time.sleep(0.4)
                go_to("medication") # Rerun to refresh the view

    st.write("---")
    # Timeline chart for patient's meds
    st.write("### Medication Schedule Timeline")
    timeline = []
    for m in patient['medications']:
        for t in m['times']:
            timeline.append({"med": m['name'], "time": t})
    if timeline:
        df_t = pd.DataFrame(timeline)
        chart = alt.Chart(df_t).mark_circle(size=90).encode(
            x='time:T',
            y=alt.Y('med:N', sort=alt.EncodingSortField(field='med')),
            tooltip=['med', 'time']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)