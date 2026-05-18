# Import libraries
import streamlit as st
from datetime import datetime, timedelta
import storage
import csv_import
import rule_engine
import notification
import reporting
import os

# Configure the Streamlit page
st.set_page_config(
    page_title="T1D Exercise Alert System",
    page_icon="🏃",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🏃 T1D Exercise Alert")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate to:",
    ["Schedule", "Check-In", "History", "Settings"]
)

# ── Schedule Page ───────────────────────────────────────────────
# ── Schedule Page ───────────────────────────────────────────────
if page == "Schedule":
    st.title("📅 Exercise Schedule")

    # Tab selection - Google Calendar or manual upload
    tab1, tab2 = st.tabs(["🔗 Connect Google Calendar", "📁 Upload .ics File"])

    # ── Tab 1: Google Calendar OAuth ────────────────────────────
    with tab1:
        st.write("Connect your Google Calendar to automatically sync exercise sessions.")

        import google_calendar

        # Check if already connected
        credentials = google_calendar.load_credentials()

        if credentials is None:
            # Not connected - show login button
            st.info("Click the button below to connect your Google Calendar.")

            if st.button("🔗 Connect Google Calendar"):
                auth_url, state = google_calendar.get_auth_url()
                st.session_state['oauth_state'] = state
                st.markdown(f"[Click here to authorize with Google]({auth_url})")
                st.warning("After authorizing, copy the code from the URL and paste it below.")
                
            # Handle OAuth callback code
            auth_code = st.text_input("Paste authorization code here:")
            if auth_code and st.button("✅ Submit Code"):
                try:
                    state = st.session_state.get('oauth_state', '')
                    credentials = google_calendar.get_credentials_from_code(
                        auth_code, state
                    )
                    st.success("Google Calendar connected successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error connecting: {e}")
        else:
            # Already connected - show sync button
            st.success("✅ Google Calendar is connected.")

            if st.button("🔄 Sync Exercise Sessions Now"):
                with st.spinner("Fetching events from Google Calendar..."):
                    try:
                        all_events, exercise_events = google_calendar.get_exercise_events_from_google(credentials)

                        st.success(f"Found {len(all_events)} total events — {len(exercise_events)} exercise sessions detected.")

                        if len(exercise_events) == 0:
                            st.warning("No exercise events found. Try adjusting your keywords in Settings.")
                        else:
                            st.subheader("Preview — Exercise Sessions Found")
                            preview_data = []
                            for event in exercise_events:
                                preview_data.append({
                                    "Title": event.get("title", ""),
                                    "Start": str(event.get("start", "")),
                                    "End": str(event.get("end", ""))
                                })
                            st.dataframe(preview_data, width="stretch")

                            if st.button("✅ Confirm Import"):
                                storage.create_tables()
                                saved = 0
                                skipped = 0
                                for event in exercise_events:
                                    start = event.get("start")
                                    end = event.get("end")
                                    title = event.get("title", "")
                                    alert_time = start - timedelta(minutes=30)
                                    result = storage.save_session(title, start, end, alert_time)
                                    if result:
                                        saved += 1
                                    else:
                                        skipped += 1
                                st.success(f"Import complete! {saved} sessions saved, {skipped} duplicates skipped.")
                    except Exception as e:
                        st.error(f"Error syncing calendar: {e}")

            if st.button("🔓 Disconnect Google Calendar"):
                if os.path.exists('token.json'):
                    os.remove('token.json')
                st.success("Google Calendar disconnected.")
                st.rerun()

    # ── Tab 2: Manual Upload ─────────────────────────────────────
    with tab2:
        st.write("Upload your Google Calendar export to import exercise sessions.")

        uploaded_file = st.file_uploader(
            "Upload your calendar file (.ics)",
            type=["ics"]
        )

        if uploaded_file is not None:
            with open("temp_calendar.ics", "wb") as f:
                f.write(uploaded_file.getbuffer())

            all_events, exercise_events = csv_import.get_exercise_events("temp_calendar.ics")

            st.success(f"Found {len(all_events)} total events — {len(exercise_events)} exercise sessions detected.")

            if len(exercise_events) == 0:
                st.warning("No exercise events found. Try adjusting your keywords in Settings.")
            else:
                st.subheader("Preview — Exercise Sessions Found")
                preview_data = []
                for event in exercise_events:
                    preview_data.append({
                        "Title": event.get("title", ""),
                        "Start": str(event.get("start", "")),
                        "End": str(event.get("end", ""))
                    })
                st.dataframe(preview_data, width="stretch")

                if st.button("✅ Confirm Import"):
                    storage.create_tables()
                    saved = 0
                    skipped = 0
                    for event in exercise_events:
                        start = event.get("start")
                        end = event.get("end")
                        title = event.get("title", "")
                        alert_time = start - timedelta(minutes=30)
                        result = storage.save_session(title, start, end, alert_time)
                        if result:
                            saved += 1
                        else:
                            skipped += 1
                    st.success(f"Import complete! {saved} sessions saved, {skipped} duplicates skipped.")

# ── Check-In Page ───────────────────────────────────────────────
elif page == "Check-In":
    st.title("🩸 Pre-Exercise Glucose Check-In")
    st.write("Enter your current blood glucose reading before exercise.")

    glucose = st.number_input(
        "Blood glucose level (mg/dL)",
        min_value=40,
        max_value=400,
        value=120,
        step=1
    )

    if st.button("🔍 Check Glucose"):
        result = rule_engine.classify_glucose(glucose)
        color = rule_engine.get_zone_color(result['zone'])

        # Display classification
        st.markdown("---")
        st.subheader(f"Result: {result['classification']}")
        st.info(f"📋 {result['recommendation']}")

        # Color coded zone indicator
        if color == 'green':
            st.success(f"Zone {result['zone']} — {result['classification']}")
        elif color in ['red', 'purple']:
            st.error(f"Zone {result['zone']} — {result['classification']}")
        elif color in ['orange', 'yellow']:
            st.warning(f"Zone {result['zone']} — {result['classification']}")
        else:
            st.info(f"Zone {result['zone']} — {result['classification']}")

        # Send caregiver alert if needed
        if result['alert_caregiver']:
            st.warning("⚠️ Caregiver has been notified.")
            # Load settings to get child name and CGM status
            settings = storage.get_settings()
            notification.send_sms(
                f"T1D Glucose Alert: {settings['child_name']}'s pre-exercise glucose is {glucose} mg/dL. "
                f"Classification: {result['classification']}. "
                f"Recommended action: {result['recommendation']}."
                + (f" Reminder: Set {settings['child_name']}'s CGM to Activity Mode "
                   f"to reduce hypoglycemia during and/or after exercise."
                   if settings['has_cgm'] else "")
            )

        # Save reading to database
        storage.save_glucose(1, glucose, result['classification'])
        st.caption("Reading saved to history.")


# ── History Page ────────────────────────────────────────────────
elif page == "History":
    st.title("📊 Session History")
    storage.create_tables()

    # Sessions table
    st.subheader("Exercise Sessions")
    sessions = storage.get_all_sessions()

    if len(sessions) == 0:
        st.info("No sessions imported yet. Go to the Schedule page to import your calendar.")
    else:
        session_data = []
        for s in sessions:
            session_data.append({
                "ID": s[0],
                "Title": s[1],
                "Start": s[2],
                "End": s[3],
                "Alert Time": s[4],
                "Imported": s[5]
            })
        st.dataframe(session_data, width='stretch')

    st.markdown("---")

    # Glucose readings table
    st.subheader("Glucose Readings")
    readings = storage.get_glucose_readings()

    if len(readings) == 0:
        st.info("No glucose readings recorded yet. Go to the Check-In page to log a reading.")
    else:
        reading_data = []
        for r in readings:
            reading_data.append({
                "ID": r[0],
                "Session ID": r[1],
                "Glucose (mg/dL)": r[2],
                "Classification": r[3],
                "Recorded At": r[4]
            })
        st.dataframe(reading_data, width='stretch')

    # Trend charts - only in History page
    st.markdown("---")
    st.subheader("📈 Glucose Trends")

    fig1 = reporting.plot_glucose_trend()
    fig2 = reporting.plot_zone_distribution()

    if fig1 is not None:
        st.pyplot(fig1)
    if fig2 is not None:
        st.pyplot(fig2)


# ── Settings Page ───────────────────────────────────────────────
elif page == "Settings":
    st.title("⚙️ Settings")
    st.write("Configure your alert preferences.")

    # Load saved settings from database
    saved = storage.get_settings()

    st.subheader("Patient Information")
    child_name = st.text_input("Child/Patient name", value=saved['child_name'])
    has_cgm = st.checkbox("Uses a CGM device (Dexcom, Libre, etc.)", value=saved['has_cgm'])

    st.subheader("Alert Settings")
    alert_lead = st.slider(
        "Alert lead time (minutes before exercise)",
        min_value=10,
        max_value=60,
        value=saved['alert_lead_minutes'],
        step=5
    )

    st.subheader("Exercise Keywords")
    st.write("Sessions containing these words will be detected as exercise events.")
    keywords = st.text_area(
        "Keywords (one per line)",
        value="gym\nrun\nworkout\nsoccer\nswim\npractice\nexercise\nyoga\nbike\nwalk\ntennis\nbasketball\nfootball\ntraining"
    )

    if st.button("💾 Save Settings"):
        storage.save_settings(child_name, has_cgm, alert_lead)
        st.success(f"Settings saved! Alerts will fire {alert_lead} minutes before each session.")
        if has_cgm:
            st.info(f"CGM Activity Mode reminder will be included in alerts for {child_name}.")
