import streamlit as st
from database import init_db
from views.plan import render_plan
from views.track import render_track
from views.reflect import render_reflect
from views.dashboard import render_dashboard
from views.insights import render_insights
from views.settings import render_settings
from views.help import render_help
from models import get_setting
from auth import verify_google_oauth, logout

# Initialize database
init_db()

st.set_page_config(page_title="Daylytics", page_icon="📈", layout="centered")

user_info = verify_google_oauth()

if user_info:
    user_email = user_info['email']
    with st.sidebar:
        st.write(f"Logged in as: **{user_info['name']}**")
        st.write(f"*{user_email}*")
        if st.button("Log Out"):
            logout()
            
    st.title("📈 Daylytics")

    default_mode = get_setting(user_email, "default_mode")

    if default_mode is None:
        render_settings(user_email, onboarding=True)
    else:
        tabs = st.tabs(["📋 Plan", "⏱ Track", "🌅 Reflect", "📊 Dashboard", "💡 Insights", "⚙️ Settings", "❓ Help"])
        
        with tabs[0]:
            render_plan(user_email)
        with tabs[1]:
            render_track(user_email)
        with tabs[2]:
            render_reflect(user_email)
        with tabs[3]:
            render_dashboard(user_email)
        with tabs[4]:
            render_insights(user_email)
        with tabs[5]:
            render_settings(user_email, onboarding=False)
        with tabs[6]:
            render_help()
