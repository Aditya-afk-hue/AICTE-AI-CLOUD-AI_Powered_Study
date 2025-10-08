# app.py
import streamlit as st
from ai_client import AIClient
from planner import validate_inputs, build_prompt

st.set_page_config(page_title="Student AI Travel Planner", layout="wide")

st.title("🎒 Student AI Travel Planner")

with st.form("planner_form"):
    destination = st.text_input("Destination", placeholder="e.g., Ooty, Goa, Jaipur")
    start_date = st.date_input("Start date (optional)", value=None)
    duration_days = st.number_input("Duration (days)", min_value=1, max_value=14, value=3)
    budget_level = st.selectbox("Budget level", ["tight", "moderate", "flexible"])
    transport = st.selectbox("Preferred transport", ["bus/train", "shared cab", "flight"])
    stay_type = st.selectbox("Preferred stay", ["hostel", "homestay", "budget hotel"])
    interests = st.text_input("Interests (comma-separated)", placeholder="nature, food, culture, hiking")
    submitted = st.form_submit_button("Generate Itinerary")

if submitted:
    ok, msg, normalized = validate_inputs({
    "destination": destination,
    "start_date": str(start_date),
    "duration_days": duration_days,
    "budget_level": budget_level,
    "interests": interests,
    "transport": transport,
    "stay_type": stay_type
})
    if not ok:
        st.error(msg)
    else:
        prompt = build_prompt(normalized)
        try:
            client = AIClient()
            result = client.generate_itinerary(prompt)
            # st.subheader("📋 JSON Itinerary")
            # st.json(result["itinerary_json"])
            st.subheader("📝 Summary")
            st.write(result["summary_text"])
        except Exception as e:
            st.error(f"Error: {e}")