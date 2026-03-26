import streamlit as st
import datetime
from models import get_tasks_by_date, save_reflection, get_reflection_by_date

def calculate_score(tasks):
    weights = {"High": 3, "Medium": 2, "Low": 1}
    
    total_planned = sum(weights[t['priority']] for t in tasks)
    if total_planned == 0:
        return 0.0
        
    completed_weighted = sum(weights[t['priority']] for t in tasks if t['status'] == 'Completed')
    skipped_high = sum(1 for t in tasks if t['status'] == 'Skipped' and t['priority'] == 'High')
    
    # Score penalty logic as described
    score = ((completed_weighted - (skipped_high * 3)) / total_planned) * 100
    return max(0.0, min(100.0, score))

def render_reflect(user_email):
    st.header("End-of-Day Reflection")
    
    selected_date = st.date_input("Date", datetime.date.today(), key="reflect_date")
    date_str = selected_date.isoformat()
    
    tasks = get_tasks_by_date(user_email, date_str)
    
    if not tasks:
        st.info("No tasks planned for this date. Go to the Plan tab to add some.")
        return
        
    completed = [t for t in tasks if t['status'] == 'Completed']
    skipped = [t for t in tasks if t['status'] == 'Skipped']
    pending = [t for t in tasks if t['status'] == 'Pending']
    
    total_planned_time = sum(t['est_time_mins'] for t in tasks)
    total_actual_time = sum(t['actual_time_mins'] for t in tasks)
    
    score = calculate_score(tasks)
    
    st.subheader("Daily Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tasks Completed", len(completed), f"{len(completed)}/{len(tasks)}")
    col2.metric("Tasks Skipped", len(skipped))
    col3.metric("Time Planned", f"{total_planned_time} m")
    col4.metric("Actual Time", f"{total_actual_time} m", f"{total_actual_time - total_planned_time} m")
    
    st.write("---")
    st.metric("Productivity Score", f"{score:.1f}%")
    
    if pending:
        return
        
    existing_reflection = get_reflection_by_date(user_email, date_str)
    
    st.subheader("Your Reflection")
    with st.form("reflection_form"):
        mood = st.slider("Mood (1=Terrible, 5=Excellent)", 1, 5, existing_reflection['mood'] if existing_reflection else 3)
        energy = st.slider("Energy Level (1=Exhausted, 5=Energized)", 1, 5, existing_reflection['energy'] if existing_reflection else 3)
        notes = st.text_area("Notes", existing_reflection['notes'] if existing_reflection else "")
        
        submitted = st.form_submit_button("Save Reflection")
        if submitted:
            save_reflection(user_email, date_str, mood, energy, notes, score)
            st.success("Reflection saved successfully!")
            st.rerun()
