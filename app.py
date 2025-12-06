import streamlit as st
import pandas as pd
import numpy as np
import datetime
import heapq

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Healthcare DSA Dashboard",
    page_icon="🏥",
    layout="wide",
)

# -----------------------------
# Custom CSS (UI Enhancements)
# -----------------------------
st.markdown("""
<style>
/* Global Background */
.main { background-color: #eef2f7; }

/* Gradient Navbar */
.navbar {
    background: linear-gradient(90deg, #003566, #00509d);
    padding: 18px 30px;
    border-radius: 12px;
    margin-bottom: 25px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
}
.navbar h1 { color: #ffffff; font-size: 32px; margin: 0; }

/* Sidebar profile card */
.sidebar-card {
    text-align: center;
    padding: 15px;
    border-radius: 15px;
    background: #ffffff;
    box-shadow: 0 3px 8px rgba(0,0,0,0.1);
}
.sidebar-card img {
    width: 90px;
    border-radius: 50%;
    margin-bottom: 10px;
}

/* Section Card */
.section-card {
    background-color: white;
    padding: 22px;
    border-radius: 15px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
    margin-bottom: 22px;
    transition: transform .2s;
}
.section-card:hover { transform: translateY(-3px); }

/* Metric boxes with shimmer */
.metric-box {
    background: linear-gradient(110deg, #ffffff 40%, #f0f4ff 50%, #ffffff 60%);
    background-size: 200% 100%;
    animation: shimmer 2s infinite;
    padding: 22px;
    border-radius: 14px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
}
@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Medication pills */
.med-pill {
    background: #e8f0ff;
    padding: 8px 14px;
    border-radius: 10px;
    font-size: 14px;
    margin: 4px;
    display: inline-block;
    color: #003566;
    font-weight: 600;
}

/* Button styling */
.stButton > button {
    background: #00509d;
    color: white;
    padding: 10px 22px;
    border-radius: 10px;
    border: none;
}
.stButton > button:hover { background: #003f7d; }

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] { gap: 20px; }
.stTabs [data-baseweb="tab"] {
    background-color: #e3edff;
    border-radius: 12px;
    padding: 10px 25px;
    font-weight: 600;
    color: #003566;
}
.stTabs [data-baseweb="tab"]:hover { background-color: #d5e4ff; }

/* Footer */
.footer {
    text-align: center;
    color: #7b8a97;
    padding: 30px 10px;
    font-size: 15px;
    margin-top: 40px;
}

/* Notification badge */
.nav-badge {
    background-color: red;
    color: white;
    border-radius: 50%;
    padding: 2px 8px;
    font-size: 12px;
    margin-left: 5px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Simulated Data Generators
# -----------------------------
np.random.seed(42)
patients = [f"Patient {i}" for i in range(1, 21)]
medications = ["Aspirin", "Metformin", "Lisinopril", "Atorvastatin", "Amoxicillin"]

def generate_med_schedule():
    meds = np.random.choice(medications, size=np.random.randint(2, 5), replace=False)
    schedule = []
    for med in meds:
        times = sorted([datetime.time(np.random.randint(6, 22), np.random.choice([0, 30])) for _ in range(3)])
        schedule.append({"Medication": med, "Times": times})
    return schedule

def generate_metrics():
    readings = []
    for _ in range(np.random.randint(8, 15)):
        readings.append({
            "Heart Rate": np.random.randint(60, 100),
            "Blood Pressure": np.random.randint(110, 150),
            "Temperature": round(np.random.uniform(36.0, 38.0), 1),
            "Timestamp": datetime.datetime.now() - datetime.timedelta(hours=np.random.randint(1, 96))
        })
    return readings

patient_med_data = {p: generate_med_schedule() for p in patients}
patient_metrics = {p: generate_metrics() for p in patients}

# -----------------------------
# Header
# -----------------------------
st.markdown("""
<div class="navbar">
    <h1>🏥 Healthcare Monitoring Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Sidebar with Profile
# -----------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-card">
        <img src="https://cdn-icons-png.flaticon.com/512/2922/2922510.png">
        <h3 style='margin-bottom:5px;'>Healthcare Monitor</h3>
        <p style='font-size:13px; color:#6c757d;'>AI-powered DSA Visualization</p>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# Notification Logic
# -----------------------------
now = datetime.datetime.now().time()
current_hour = now.hour
current_minute = now.minute

active_alerts = []

for p, meds in patient_med_data.items():
    for entry in meds:
        for t in entry["Times"]:
            if t.hour == current_hour and t.minute == current_minute:
                active_alerts.append(f"Medication time NOW for {p}")
            elif (t.hour == current_hour and t.minute > current_minute) or \
                 (t.hour == current_hour + 1 and t.minute <= current_minute):
                active_alerts.append(f"Medication due soon for {p}")

# Add red badge count
notification_count = len(active_alerts)
notification_label = f"Notifications{' (' + str(notification_count) + ')' if notification_count > 0 else ''}"


# -----------------------------
# Navigation with Notification Badge
# -----------------------------
page = st.sidebar.selectbox("🔎 Navigation", ["Medication Tracker", "Health Metric Dashboard", "Notifications"], format_func=lambda x: notification_label if x=="Notifications" else x)

# -----------------------------
# Medication Tracker
# -----------------------------
if page == "Medication Tracker":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.header("💊 Medication Reminder System")
    st.write("Track patient medications and detect upcoming doses.")
    st.markdown('</div>', unsafe_allow_html=True)

    selected_patient = st.selectbox("Select Patient", patients)
    schedule = patient_med_data[selected_patient]

    st.subheader(f"📅 Medication Schedule for {selected_patient}")
    for med in schedule:
        st.markdown(f"### {med['Medication']}")
        pill_html = "".join(f'<span class="med-pill">{t.strftime("%H:%M")}</span>' for t in med["Times"])
        st.markdown(pill_html, unsafe_allow_html=True)

    # Priority queue for next dose
    now_time = datetime.datetime.now().time()
    pq = []
    for med in schedule:
        for t in med["Times"]:
            heapq.heappush(pq, (t, med["Medication"]))
    next_dose = None
    while pq:
        time_val, med_name = heapq.heappop(pq)
        if time_val > now_time:
            next_dose = (time_val, med_name)
            break

    st.markdown("---")
    if next_dose:
        st.success(f"🕒 **Next Dose:** {next_dose[1]} at **{next_dose[0].strftime('%H:%M')}**")
    else:
        st.warning("All medication times for today have passed.")

# -----------------------------
# Health Metrics Dashboard
# -----------------------------
elif page == "Health Metric Dashboard":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.header("📊 Patient Health Metrics")
    st.write("Monitor vitals like heart rate, blood pressure, and temperature.")
    st.markdown('</div>', unsafe_allow_html=True)

    selected_patient = st.selectbox("Select Patient", patients, key="metrics")
    data = pd.DataFrame(patient_metrics[selected_patient]).sort_values("Timestamp")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("❤️ Avg Heart Rate", f"{data['Heart Rate'].mean():.1f} bpm")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("🩸 Avg Blood Pressure", f"{data['Blood Pressure'].mean():.1f} mmHg")
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box">', unsafe_allow_html=True)
        st.metric("🌡 Avg Temperature", f"{data['Temperature'].mean():.1f} °C")
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("📈 Vital Trends (Last 72 Hours)")
    st.line_chart(data.set_index("Timestamp")[["Heart Rate", "Blood Pressure", "Temperature"]])

    trend = "Stable"
    if data["Heart Rate"].iloc[-1] > data["Heart Rate"].iloc[0]:
        trend = "Increasing"
    elif data["Heart Rate"].iloc[-1] < data["Heart Rate"].iloc[0]:
        trend = "Decreasing"
    st.info(f"📌 Current Heart Rate Trend: **{trend}**")

# -----------------------------
# Notifications Page
# -----------------------------
elif page == "Notifications":
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.header("🔔 Medication Notifications")
    st.write(f"Total Active Alerts: {notification_count}")
    st.markdown('</div>', unsafe_allow_html=True)

    if active_alerts:
        for alert in active_alerts:
            st.warning(f"🔔 {alert}")
    else:
        st.info("ℹ️ No current medication alerts.")

# -----------------------------
# Footer
# -----------------------------
st.markdown("""
<div class="footer">
    Healthcare DSA Dashboard — Designed with ❤️ for better visualization
</div>
""", unsafe_allow_html=True)
