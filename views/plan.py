import streamlit as st
import datetime
from models import add_task, get_tasks_by_date, update_task_details, delete_task, get_setting, add_repeating_task, get_repeating_tasks

CATEGORIES = ["Health", "Work", "Learning", "Family", "Personal"]
PRIORITIES = ["High", "Medium", "Low"]

CATEGORY_EMOJIS = {
    "Health": "🧘",
    "Work": "💼",
    "Learning": "📚",
    "Family": "👪",
    "Personal": "✨"
}

def render_plan(user_email):
    st.header("Plan Your Day")
    
    selected_date = st.date_input("Date", datetime.date.today(), key="plan_date")
    
    # Auto-allocation Logic
    default_mode = get_setting(user_email, "default_mode", "None")
    is_weekday = selected_date.weekday() < 5
    max_available_mins = 1440
    
    current_tasks = get_tasks_by_date(user_email, selected_date.isoformat())
    
    # 1. Always inject 8 hours of sleep
    has_sleep = any(t['name'] == 'Sleep' for t in current_tasks)
    if not has_sleep:
        add_task(user_email, selected_date.isoformat(), "Sleep", "Health", "High", 8 * 60, is_default=1)
        
    # 2. Inject Work/School commitment
    if default_mode in ["Work", "School"] and is_weekday:
        has_work_school = any('Time Commitment' in t['name'] for t in current_tasks)
        if not has_work_school:
            cat = "Work" if default_mode == "Work" else "Learning"
            add_task(user_email, selected_date.isoformat(), f"[{default_mode}] Time Commitment", cat, "High", 8 * 60, is_default=1)
            
    # 3. Inject repeating weekday tasks
    if is_weekday:
        rep_tasks = get_repeating_tasks(user_email)
        latest_tasks = get_tasks_by_date(user_email, selected_date.isoformat())
        for rt in rep_tasks:
            # Inject only if a task with the exact same name isn't already scheduled today
            if not any(t['name'] == rt['name'] for t in latest_tasks):
                add_task(user_email, selected_date.isoformat(), rt['name'], rt['category'], rt['priority'], rt['est_time_mins'], is_default=0)
            
    # Fetch existing tasks again after all potential injections
    existing_tasks = get_tasks_by_date(user_email, selected_date.isoformat())
    
    st.subheader("Current Plan")
    total_time = 0
    high_priority_count = 0
    has_health_personal = False
    
    if existing_tasks:
        total_time = sum(t['est_time_mins'] for t in existing_tasks)
        high_priority_count = sum(1 for t in existing_tasks if t['priority'] == 'High')
        has_health_personal = any(t['category'] in ['Health', 'Personal'] for t in existing_tasks)

        for t in existing_tasks:
            emoji = CATEGORY_EMOJIS.get(t['category'], '')
            is_def = t.get('is_default', 0) == 1
            lock_icon = "🔒 " if is_def else ""
            
            with st.expander(f"{lock_icon}{emoji} {t['name']} [{t['category']} | {t['priority']}] : {t['est_time_mins']} mins"):
                with st.form(f"edit_task_{t['id']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        edit_name = st.text_input("Name", value=t['name'], disabled=is_def)
                        edit_cat = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(t['category']), disabled=is_def)
                    with col2:
                        edit_pri = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(t['priority']), disabled=is_def)
                        edit_est = st.number_input("Est. Time", min_value=1, max_value=1440, value=t['est_time_mins'])
                    
                    if st.form_submit_button("Update Task"):
                        if not edit_name.strip():
                            st.error("Task name is required.")
                        else:
                            update_task_details(user_email, t['id'], edit_name.strip(), edit_cat, edit_pri, edit_est)
                            st.rerun()
                
                if not is_def:
                    if st.button("Delete Task", key=f"del_{t['id']}"):
                        delete_task(user_email, t['id'])
                        st.rerun()
                else:
                    st.info("This is a default time commitment block and cannot be deleted.")
                    
        st.write("---")
        
        remaining_mins = max_available_mins - total_time
        col1, col2, col3 = st.columns(3)
        col1.metric("Available Time", f"{max_available_mins//60}h {max_available_mins%60}m")
        col2.metric("Committed Time", f"{total_time//60}h {total_time%60}m")
        col3.metric("Remaining Time", f"{remaining_mins//60}h {remaining_mins%60}m", delta=remaining_mins)
        
        colA, colB, colC = st.columns(3)
        colA.info(f"**Valid Plan:** " + ("✅" if remaining_mins >= 0 else "❌ Exceeded!"))
        colB.info(f"**High Priority:** {high_priority_count}/5 " + ("✅" if high_priority_count <= 5 else "❌"))
        colC.info(f"**Health/Personal:** " + ("✅" if has_health_personal else "⚠️ (Required)"))
    else:
        st.info("No tasks planned for this date yet.")
        remaining_mins = max_available_mins

    st.divider()
    
    st.subheader("Add New Task")
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Task Name")
            category = st.selectbox("Category", CATEGORIES)
        with col2:
            priority = st.selectbox("Priority", PRIORITIES)
            est_time = st.number_input("Estimated Time (mins)", min_value=1, max_value=1440, value=30)
            
        repeat_weekdays = st.checkbox("Repeat on Weekdays")
        submitted = st.form_submit_button("Add Task")
        
        if submitted:
            if not name.strip():
                st.error("Task name is required.")
            elif total_time + est_time > max_available_mins:
                st.error(f"Validation Error: Total planned time cannot exceed daily availability ({max_available_mins//60} hours).")
            elif priority == 'High' and high_priority_count >= 5:
                st.error("Validation Error: Maximum 5 high priority tasks allowed per day.")
            else:
                add_task(user_email, selected_date.isoformat(), name.strip(), category, priority, est_time)
                if repeat_weekdays:
                    add_repeating_task(user_email, name.strip(), category, priority, est_time)
                st.success(f"Task '{name}' added successfully!")
                st.rerun()
