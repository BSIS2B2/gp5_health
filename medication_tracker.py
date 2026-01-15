import streamlit as st  # type: ignore
import pandas as pd  # type: ignore
import altair as alt  # type: ignore
from datetime import datetime
from sample_data import go_to, _parse_time


# --- Small top nav for logged-in pages ---
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

    with cols[1]:
        if st.button("Dashboard", key="nav_dash"):
            go_to("dashboard")
    with cols[2]:
        if st.button("Medication", key="nav_med"):
            go_to("medication")
    with cols[3]:
        if st.button("Profile", key="nav_profile"):
            go_to("user_info")
    with cols[4]:
        if st.button("Schedule Tracker"):
            go_to("schedule")
    with cols[5]:
        if st.button("Logout", key="nav_logout"):
            st.session_state.current_user = None
            go_to("auth")


# --- MEDICATION TRACKER PAGE ---
def medication_page():
    """Displays the medication tracking dashboard for a selected patient."""
    top_nav_bar("Medication Reminder & Tracker")
    st.write("")

    patients = st.session_state.patients

    # Patient selector
    sel = st.selectbox(
        "Select patient",
        [f"{p['id']} — {p['name']}" for p in patients],
        index=0
    )
    patient_index = next(
        i for i, p in enumerate(patients)
        if f"{p['id']} — {p['name']}" == sel
    )
    patient = patients[patient_index]


    # Aligned Quick Stats + Patient Info in one flex container
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #ffffff;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.06);
            margin-bottom: 16px;
        ">
            <div style='font-weight:600; font-size:16px; color:#0b5394;'>
                {patient['name']} — Age: {patient['age']}
            </div>
            <div style='text-align:right; font-size:14px; color:#333;'>
                <div><b>Med count:</b> {len(patient['medications'])}</div>
                <div><b>Readings:</b> {len(patient['readings'])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("---")

    # Medication List (with Status)
    med_rows = []
    for m in patient['medications']:
        med_rows.append({
            "Medication": m['name'],
            "Dose": m['dose'],
            "Times": ", ".join(m['times']),
            "Last taken": m['last_taken'] or "—",
            "Status": "Taken" if m['last_taken'] else "Pending"
        })

    st.write("### Medication List (with Status)")
    st.dataframe(pd.DataFrame(med_rows), use_container_width=True)

    st.write("---")

    # Medications Already Taken
    st.write("### Medications Already Taken")

    taken_rows = []
    now = datetime.now()

    for i, m in enumerate(patient['medications']):
        if m['last_taken']:
            taken_rows.append({
                "Medication": m['name'],
                "Dose": m['dose'],
                "Times": ", ".join(m['times']),
                "Taken at": m['last_taken']
            })
        else:
            # Example taken data per patient
            example_time = now.replace(hour=8 + i, minute=0).strftime("%Y-%m-%d %H:%M")
            taken_rows.append({
                "Medication": m['name'],
                "Dose": m['dose'],
                "Times": ", ".join(m['times']),
                "Taken at": example_time
            })

    st.info(
        f" **Patient:** {patient['name']} — showing taken medications (sample times used where data is missing)."
    )

    df_taken = pd.DataFrame(taken_rows)
    st.dataframe(df_taken, use_container_width=True)

    st.write("---")

    # Timeline chart
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