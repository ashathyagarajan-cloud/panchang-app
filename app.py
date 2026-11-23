import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="Panchang Clock Dashboard", layout="centered")
st.title("🕒 Panchang Clock Dashboard v2")

# Load data from GitHub using Secrets for security
@st.cache_data
def load_data(token):
    url = "https://api.github.com/repos/ashathyagarajan-cloud/myData/contents/panchang-all-timings.csv"
    return pd.read_csv(
        url,
        storage_options={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.raw",
        },
    )

# Securely fetch GitHub Token from deployment platform environment secrets
github_token = st.secrets.get("GITHUB_TOKEN") if "GITHUB_TOKEN" in st.secrets else None

if not github_token:
    github_token = st.sidebar.text_input("Enter GitHub Token:", type="password")

if github_token:
    try:
        data = load_data(github_token)
        unique_dates = sorted(data['Date'].unique())

        # Current date and time in the panchang's time zone (the server itself runs on UTC)
        now = datetime.now(ZoneInfo("America/Chicago"))
        current_date = now.strftime("%Y-%m-%d")

        selected_date = st.selectbox(
            "Select Date:",
            options=unique_dates,
            index=unique_dates.index(current_date) if current_date in unique_dates else 0
        )

        # Time picker made of three dropdowns: hour, minute, AM/PM
        st.write("Query Time:")
        col1, col2, col3 = st.columns(3)
        hour = col1.selectbox("Hour", [f"{h:02d}" for h in range(1, 13)],
                              index=int(now.strftime("%I")) - 1, key="hour")
        minute = col2.selectbox("Minute", [f"{m:02d}" for m in range(60)],
                                index=now.minute, key="minute")
        ampm = col3.selectbox("AM/PM", ["AM", "PM"],
                              index=0 if now.strftime("%p") == "AM" else 1, key="ampm")
        target_time_str = f"{hour}:{minute}:00 {ampm}"

        if st.button("Check Active Period", type="primary"):
            day_data = data[data['Date'] == selected_date].copy()
            if day_data.empty:
                st.warning(f"No data available for the date: {selected_date}")
            else:
                try:
                    target_time = datetime.strptime(target_time_str.strip(), "%I:%M:%S %p").time()
                    active_events = []

                    for idx, row in day_data.iterrows():
                        try:
                            start_time = datetime.strptime(row['Start'].strip(), "%I:%M:%S %p").time()
                            end_time = datetime.strptime(row['End'].strip(), "%I:%M:%S %p").time()

                            if start_time <= end_time:
                                if start_time <= target_time <= end_time:
                                    active_events.append(row['Timing'])
                            else:
                                if target_time >= start_time or target_time <= end_time:
                                    active_events.append(row['Timing'])
                        except:
                            continue

                    if active_events:
                        st.success(f"At **{target_time_str}** on **{selected_date}**, the active status/timing is: **{', '.join(active_events)}**")
                    else:
                        st.info(f"No matching scheduled event found for {target_time_str} on {selected_date}.")
                except ValueError:
                    st.error("Invalid Time format.")
    except Exception as e:
        st.error(f"Failed to load data: {e}")
else:
    st.info("Please provide your GitHub Token in the sidebar or application secrets configuration.")
