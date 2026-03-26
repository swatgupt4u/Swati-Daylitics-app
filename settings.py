import streamlit as st
from models import get_setting, set_setting, get_repeating_tasks, delete_repeating_task

def render_settings(user_email, onboarding=False):
    if onboarding:
        st.header("Welcome to Daylytics! 👋")
        st.write("To get started, please select your primary lifestyle. This helps us automatically adjust your available planning time.")
    else:
        st.header("Settings")
        st.write("Update your time commitment preferences below.")
        
    current_mode = get_setting(user_email, "default_mode", "None")
    # If None on fetch but basically we enforce a choice
    if current_mode not in ["Work", "School", "None"]:
        current_mode = "None"
        
    with st.form("settings_form"):
        mode = st.radio(
            "Default Time Commitment Mode",
            ["Work", "School", "None"],
            index=["Work", "School", "None"].index(current_mode),
            help="Work and School will automatically reserve 8 hours on weekdays."
        )
        submit = st.form_submit_button("Save & Continue" if onboarding else "Save Settings")
        
        if submit:
            set_setting(user_email, "default_mode", mode)
            st.success("Preferences saved!")
            st.rerun()

    if not onboarding:
        st.divider()
        st.subheader("Manage Repeating Weekday Tasks")
        rep_tasks = get_repeating_tasks(user_email)
        if rep_tasks:
            for rt in rep_tasks:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"🔄 **{rt['name']}** [{rt['category']}] - {rt['est_time_mins']} mins")
                with col2:
                    if st.button("Delete", key=f"del_rep_{rt['id']}"):
                        delete_repeating_task(user_email, rt['id'])
                        st.rerun()
        else:
            st.info("You don't have any weekday repeating tasks scheduled.")
