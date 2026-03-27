import streamlit as st

def render_help():
    st.header("❓ App Guide & Help")
    
    with st.expander("🚀 What is Daylytics?", expanded=True):
        st.write("""
        **Daylytics** is your personal command center for intentional productivity. 
        Unlike simple to-do lists, Daylytics focuses on the **Plan-Track-Reflect** cycle 
        to help you understand your energy patterns and improve your focus over time.
        """)

    st.subheader("🛠 How to Use Daylytics Effectively")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 1. Plan")
        st.write("""
        **When:** Every morning or the night before.
        
        **Strategy:**
        - **Limit High Priority:** Stick to max 3-5 critical tasks.
        - **Balance Categories:** Ensure you have at least one 'Health' or 'Personal' task.
        - **Realistic Estimations:** Don't overfill your 24h budget.
        """)
        
    with col2:
        st.markdown("### 2. Track")
        st.write("""
        **When:** Throughout the day.
        
        **Strategy:**
        - **Timer vs. Manual:** Use the 'Track' tab to record actual minutes spent.
        - **Update Status:** Mark tasks as 'Completed' or 'Skipped' as you go.
        - **Stay Honest:** Recording 'Actual Mins' helps you plan better tomorrow.
        """)
        
    with col3:
        st.markdown("### 3. Reflect")
        st.write("""
        **When:** End of your day.
        
        **Strategy:**
        - **Score Your Day:** High-priority tasks have a bigger impact on your score.
        - **Mindset Check:** Record your mood and energy.
        - **Analyze Trends:** Use the 'Insights' tab to see how energy affects your output.
        """)

    st.divider()
    
    st.subheader("📈 Understanding Your Productivity Score")
    st.info("""
    Your score is calculated based on **weighted completion**:
    - **High Priority**: 3 points
    - **Medium Priority**: 2 points
    - **Low Priority**: 1 point
    
    ⚠️ *Warning: Skipping a High Priority task subtracts 3 points from your potential score!*
    """)

    st.subheader("💡 Pro Tips")
    st.success("""
    - **Repeating Tasks**: Use the 'Settings' tab to add tasks you do every day (like Exercise or Email). They will auto-appear on your daily plan!
    - **Default Mode**: Set your 'Default Mode' to Work or School to automatically block out 8 hours on weekdays.
    """)
