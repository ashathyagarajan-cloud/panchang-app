
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Panchang Clock Dashboard", layout="centered")
st.title("🕒 Panchang Clock Dashboard")

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

        # Default values from local browser time
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time_str = datetime.now().strftime("%I:%M:%S %p")

        selected_date = st.selectbox(
            "Select Date:", 
            options=unique_dates,
            index=unique_dates.index(current_date) if current_date in unique_dates else 0
        )
        
        target_time_str = st.text_input("Query Time:", value=current_time_str, placeholder="HH:MM:SS AM/PM")

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
                    st.error("Invalid Time format. Please use 'HH:MM:SS AM/PM' (e.g., 10:19:30 AM)")
    except Exception as e:
        st.error(f"Failed to load data: {e}")
else:
    st.info("Please provide your GitHub Token in the sidebar or application secrets configuration.")
