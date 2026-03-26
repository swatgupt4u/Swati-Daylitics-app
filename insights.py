import streamlit as st
import pandas as pd
from models import get_recent_reflections, get_recent_tasks

def generate_ai_suggestions(tasks_df, ref_df):
    suggestions = []
    
    if not tasks_df.empty:
        high_skipped = tasks_df[(tasks_df['priority'] == 'High') & (tasks_df['status'] == 'Skipped')]
        if len(high_skipped) > 2:
            suggestions.append("💡 **Prioritization:** You frequently skip high-priority tasks. Try scheduling them first thing in the morning when your energy might be higher.")
            
        health_personal = tasks_df[tasks_df['category'].isin(['Health', 'Personal'])]
        if len(health_personal) < 3:
            suggestions.append("🧘 **Wellbeing:** You've had few Health or Personal tasks recently. Remember to make time for yourself to avoid burnout.")

        zero_est_tasks = tasks_df[tasks_df['est_time_mins'] == 0]
        if not zero_est_tasks.empty:
            comp_zero = zero_est_tasks[zero_est_tasks['status'] == 'Completed']
            if len(comp_zero) > 0:
                suggestions.append("⚡ **Quick Wins:** You've completed tasks with 0 estimated time! Even quick tasks contribute nicely to your overall productivity.")
            
    if not ref_df.empty and not tasks_df.empty:
        daily_tasks = tasks_df.groupby('date').size().reset_index(name='task_count')
        merged = pd.merge(ref_df, daily_tasks, on='date')
        if not merged.empty:
            low_energy_days = merged[merged['energy'] <= 2]
            if not low_energy_days.empty and low_energy_days['task_count'].mean() > 5:
                suggestions.append("📉 **Energy:** On days you feel exhausted, you tend to schedule many tasks. Try planning lighter days when recovering.")
                
        if ref_df['mood'].mean() < 3:
            suggestions.append("❤️ **Mood:** Your mood has been lower than average. Consider taking a break or doing more activities you enjoy.")
            
    if not suggestions:
        suggestions.append("✨ You're doing great! Keep up the good work and maintain your balance.")
        
    return suggestions

def render_insights(user_email):
    st.header("Weekly Insights & AI Suggestions")
    st.write("Analyzing your last 7 days of activity.")
    
    tasks = get_recent_tasks(user_email, 7)
    reflections = get_recent_reflections(user_email, 7)
    
    if not tasks and not reflections:
        st.info("Not enough data to generate insights yet. Start using the app daily!")
        return
        
    tasks_df = pd.DataFrame(tasks) if tasks else pd.DataFrame()
    ref_df = pd.DataFrame(reflections) if reflections else pd.DataFrame()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Productivity Trend")
        if not ref_df.empty and 'productivity_score' in ref_df.columns:
            ref_df = ref_df.sort_values('date')
            chart_data = ref_df[['date', 'productivity_score']].set_index('date')
            st.line_chart(chart_data)
        else:
            st.write("No reflection data available for chart.")
            
    with col2:
        st.subheader("Mood & Energy Trend")
        if not ref_df.empty and 'mood' in ref_df.columns:
            chart_data = ref_df[['date', 'mood', 'energy']].set_index('date')
            st.line_chart(chart_data)
        else:
            st.write("No reflection data available for chart.")
            
    st.divider()
    
    st.subheader("🤖 AI Patterns & Suggestions")
    suggestions = generate_ai_suggestions(tasks_df, ref_df)
    
    for s in suggestions:
        st.info(s)
