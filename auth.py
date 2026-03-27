import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
import secrets

# Google OAuth Endpoints
AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
SCOPE = "openid email profile"

def verify_google_oauth():
    """ Returns user dict if authenticated, else None """
    if "user_email" in st.session_state:
        return {"email": st.session_state.user_email, "name": st.session_state.get("user_name", "User")}

    try:
        client_id = st.secrets["GOOGLE_CLIENT_ID"]
        client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
        redirect_uri = st.secrets["REDIRECT_URI"]
    except KeyError as e:
        st.error(f"Missing secret: {e}. Please add it to Streamlit Secrets.")
        return None

    # Handle OAuth callback
    query_params = st.query_params
    
    if "code" in query_params:
        code = query_params["code"]
        state = query_params.get("state")
        
        saved_state = st.session_state.get("oauth_state")
        
        # Consistent check for state persistence
        if (state and saved_state and state == saved_state) or (code and not saved_state):
            st.query_params.clear()
            
            try:
                client = OAuth2Session(client_id, client_secret, scope=SCOPE, redirect_uri=redirect_uri)
                token = client.fetch_token(TOKEN_URL, code=code)
                
                user_info_response = client.get(USER_INFO_URL)
                if user_info_response.status_code == 200:
                    user_info = user_info_response.json()
                    if "email" in user_info:
                        st.session_state.user_email = user_info["email"]
                        st.session_state.user_name = user_info.get("name", "User")
                        st.session_state.pop("oauth_state", None)
                        st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
                return None
        else:
            st.error("Session expired or access denied. Please try logging in again.")
            st.session_state.pop("oauth_state", None)
            st.query_params.clear()

    # Render Login UI
    st.title("Welcome to Daylytics 📈")
    st.write("Please sign in to manage your tasks securely.")

    if "oauth_state" not in st.session_state:
        st.session_state.oauth_state = secrets.token_urlsafe(16)

    client = OAuth2Session(client_id, scope=SCOPE, redirect_uri=redirect_uri, state=st.session_state.oauth_state)
    
    # Use prompt="consent" which is less likely to trigger 403 robot than "select_account"
    # because it forces a different Google UI flow that ignores some cookie blocks.
    authorization_url, _ = client.create_authorization_url(AUTHORIZATION_BASE_URL, prompt="consent")

    # Use a bigger, clearer button
    st.link_button("Sign in with Google", authorization_url, type="primary", use_container_width=True)
    
    st.info("💡 Note for Safari/Incognito: If you see a 403 error, please try using Chrome or a regular browser window.")

    return None

def logout():
    st.session_state.clear()
    st.rerun()
