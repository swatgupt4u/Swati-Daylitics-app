import streamlit as st
import datetime
from models import get_tasks_by_date, update_task_status
from views.plan import CATEGORY_EMOJIS

def render_track(user_email):
    st.header("Track Your Tasks")
    
    selected_date = st.date_input("Date", datetime.date.today(), key="track_date")
    tasks = get_tasks_by_date(user_email, selected_date.isoformat())
    
    if not tasks:
        st.info("No tasks planned for this date.")
        return
        
    # Define column headers for clarity
    cols = st.columns([3, 2, 2, 1])
    cols[0].markdown("**Task Information**")
    cols[1].markdown("**Status**")
    cols[2].markdown("**Actual (m)**")
    cols[3].markdown("**Save**")
    
    for task in tasks:
        emoji = CATEGORY_EMOJIS.get(task['category'], '')
        
        with st.form(f"update_task_{task['id']}"):
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                st.markdown(f"**{emoji} {task['name']}**")
                st.caption(f"{task['category']} | {task['priority']} | Est: {task['est_time_mins']}m")
            with cols[1]:
                new_status = st.selectbox("Status", ["Pending", "Completed", "Skipped"], index=["Pending", "Completed", "Skipped"].index(task['status']), label_visibility="collapsed")
            with cols[2]:
                actual_time = st.number_input("Actual Time (mins)", min_value=0, max_value=1440, value=task['actual_time_mins'], label_visibility="collapsed")
            with cols[3]:
                submitted = st.form_submit_button("Update")
            
            if submitted:
                # Apply logic to default times based on status
                if new_status in ["Pending", "Skipped"]:
                    final_time = 0
                elif new_status == "Completed" and actual_time == task['actual_time_mins']:
                    final_time = task['est_time_mins']
                else:
                    final_time = actual_time
                    
                update_task_status(user_email, task['id'], new_status, final_time)
                st.success("Task updated!")
                st.rerun()
