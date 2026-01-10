# sample_data.py
import streamlit as st # type: ignore
import random
from datetime import datetime, timedelta


# --- Shared Data ---
MEDS = [
    "Aspirin", "Metformin", "Lisinopril", "Atorvastatin",
    "Amlodipine", "Omeprazole", "Levothyroxine", "Simvastatin"
]

# --- Helpers ---
def go_to(page_name):
    """Sets the session state to navigate to a new page."""
    st.session_state.page = page_name
    # Streamlit automatically reruns, no need for explicit rerun

def is_authenticated():
    """Checks if a user is currently logged in."""
    return st.session_state.current_user is not None

def _parse_time(tstr):
    """Parses a time string into a datetime object."""
    try:
        return datetime.strptime(tstr, "%Y-%m-%d %H:%M")
    except:
        return None

# --- Data Generation ---
def random_schedule_times(count=3):
    """Generates random upcoming/past schedule times."""
    now = datetime.now().replace(second=0, microsecond=0)
    times = []
    for _ in range(count):
        t = (now + timedelta(hours=random.randint(-24, 72),
                             minutes=random.choice([0,15,30,45]))).strftime("%Y-%m-%d %H:%M")
        times.append(t)
    return sorted(list(set(times)))[:count]

def generate_sample_patients(n=25):
    """Generates a list of sample patient data."""
    patients = []
    for i in range(n):
        meds_count = random.randint(3,5)
        meds = []
        for j in range(meds_count):
            med = {
                "name": random.choice(MEDS),
                "dose": f"{random.randint(1,2)} tablet(s)",
                "times": random_schedule_times(count=random.randint(2,4)),
                "last_taken": None
            }
            meds.append(med)
        readings = []
        for k in range(random.randint(5,10)):
            readings.append({
                "hr": random.randint(55,110),
                "bp_sys": random.randint(100,150),
                "bp_dia": random.randint(60,95),
                "temp": round(random.uniform(36.0,38.2),1),
                "time": (datetime.now() - timedelta(hours=random.randint(0,72))).strftime("%Y-%m-%d %H:%M")
            })
        patients.append({
            "id": f"PT{1000+i}",
            "name": f"Patient {i+1}",
            "age": random.randint(20,85),
            "medications": meds,
            "readings": readings
        })
    return patients

