import streamlit as st
import pandas as pd
import datetime
from models import get_recent_tasks

def render_dashboard(user_email): # Added user_email parameter
    st.header("Weekly Overview") # Changed header
    
    # Removed date input and changed model function call
    tasks = get_recent_tasks(user_email, 7) 
    
    if not tasks:
        st.info("No tasks recorded for this date.")
        return
        
    df = pd.DataFrame(tasks)
    
    st.subheader("Time Distribution by Category")
    category_summary = df.groupby('category')['est_time_mins'].sum().reset_index()
    # We set index to category for Streamlit's native bar_chart
    st.bar_chart(category_summary.set_index('category'))
    
    st.subheader("Planned vs Actual Time")
    total_planned = int(df['est_time_mins'].sum())
    total_actual = int(df['actual_time_mins'].sum())
    
    col1, col2 = st.columns(2)
    col1.metric("Total Planned Time", f"{total_planned} mins")
    col2.metric("Total Actual Time", f"{total_actual} mins", delta=f"{total_actual - total_planned} mins")
    
    st.write("---")
    st.subheader("All Tasks")
    st.dataframe(df[['name', 'category', 'priority', 'status', 'est_time_mins', 'actual_time_mins']])
