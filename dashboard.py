# dashboard.py
import streamlit as st # type: ignore
import pandas as pd # type: ignore
import altair as alt # type: ignore
from datetime import datetime
# Assuming medication_tracker.py is in the same directory and contains top_nav_bar()
from medication_tracker import top_nav_bar
from schedtracker import schedule_tracker_page  # ✅ IMPORT Schedule Tracker


# --- DASHBOARD PAGE ---
def dashboard():
    """Displays the health metric dashboard for selected patients."""
    top_nav_bar("Health Metric Dashboard")
    st.write("")  # spacing
    st.write("---")  # spacing

    patients = st.session_state.patients
    patient_choices = {f"{p['id']} — {p['name']}": p for p in patients}
    
    # Multiselect for patient filtering
    sel_keys = st.multiselect(
        "Select patients to include", 
        list(patient_choices.keys()), 
        default=list(patient_choices.keys())[:5]
    )

    if not sel_keys:
        st.info("Select at least one patient to view metrics.")
        return

    # gather readings from selected patients
    records = []
    for key in sel_keys:
        p = patient_choices[key]
        for r in p['readings']:
            records.append({
                "patient": p['name'],
                # Convert time string to datetime object
                "time": datetime.strptime(r['time'], "%Y-%m-%d %H:%M"), 
                "hr": r['hr'],
                "bp_sys": r['bp_sys'],
                "bp_dia": r['bp_dia'],
                "temp": r['temp']
            })
    df = pd.DataFrame(records)
    if df.empty:
        st.warning("No readings available.")
        return

    st.write("### Combined Vitals Table (Most Recent First)")
    # Data structure usage: DataFrame sorting
    st.dataframe(df.sort_values("time", ascending=False).reset_index(drop=True), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")
    
    # Aggregation: averages
    st.write("### 📈 Aggregations (Averages)")
    avg = df.groupby("patient")[["hr","bp_sys","bp_dia","temp"]].mean().round(1).reset_index()
    st.table(avg)
    
    st.write("### Heart Rate Trend Over Time")
    hr_chart = alt.Chart(df).mark_line(point=True).encode(
        x='time:T',
        y='hr:Q',
        color='patient:N',
        tooltip=['patient','time','hr']
    ).properties(height=320)
    st.altair_chart(hr_chart, use_container_width=True)

    st.write("### Simple Trend Detection (Last 3 HR Readings)")
    trends = []
    # Trend detection uses comparison of the newest reading against the oldest in a small window (last 3)
    for key in sel_keys:
        pname = patient_choices[key]['name']
        # Uses DataFrame slicing and sorting for time-series analysis
        p_df = df[df['patient'] == pname].sort_values('time', ascending=False).head(3)
        if len(p_df) < 2:
            trend = "not enough data"
        else:
            hr_vals = p_df['hr'].values
            # hr_vals[0] is the newest, hr_vals[-1] is the oldest of the last 3
            if hr_vals[0] > hr_vals[-1]:
                trend = "**increasing** ⬆️"
            elif hr_vals[0] < hr_vals[-1]:
                trend = "**decreasing** ⬇️"
            else:
                trend = "stable ➡️"
        trends.append({"patient": pname, "hr_trend": trend})
    st.table(pd.DataFrame(trends))


