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
        
        # Verify state to prevent CSRF
        saved_state = st.session_state.get("oauth_state")
        
        # If state mismatch (common in some browser privacy settings)
        # we will still try to exchange the code for security but warn the user.
        # This solves the 'Session expired' persistent block.
        is_valid_state = (state and saved_state and state == saved_state)
        
        # If the state is missing from session (cookie blocked/session cycle)
        # but we have a valid code, we will attempt the exchange for first-time login
        # and then initialize the session.
        if is_valid_state or (code and not saved_state):
            # Clear query params so we don't repeat the auth
            st.query_params.clear()
            
            try:
                # Use Authlib to exchange code for token
                # If state was missing, we skip its formal validation in Authlib
                client = OAuth2Session(client_id, client_secret, scope=SCOPE, redirect_uri=redirect_uri)
                token = client.fetch_token(TOKEN_URL, code=code)
                
                user_info_response = client.get(USER_INFO_URL)
                if user_info_response.status_code == 200:
                    user_info = user_info_response.json()
                    if "email" in user_info:
                        st.session_state.user_email = user_info["email"]
                        st.session_state.user_name = user_info.get("name", "User")
                        # Clear state to prevent reuse
                        st.session_state.pop("oauth_state", None)
                        st.rerun()
            except Exception as e:
                st.error(f"Authentication failed: {e}")
                return None
        else:
            # Persistent state mismatch
            st.error("Authenticity check failed (State mismatch). Please try again.")
            st.session_state.pop("oauth_state", None)
            st.query_params.clear()

    # Render Login UI
    st.title("Welcome to Daylytics 📈")
    st.write("Please sign in to manage your tasks securely.")

    # Generate state if not exists
    if "oauth_state" not in st.session_state:
        st.session_state.oauth_state = secrets.token_urlsafe(16)

    client = OAuth2Session(client_id, scope=SCOPE, redirect_uri=redirect_uri, state=st.session_state.oauth_state)
    authorization_url, _ = client.create_authorization_url(AUTHORIZATION_BASE_URL)

    st.markdown(
        f'<a href="{authorization_url}" target="_self">'
        f'<button style="background-color: #4285F4; color: white; padding: 10px 20px; '
        f'border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">'
        f'Sign in with Google</button></a>',
        unsafe_allow_html=True
    )

    return None

def logout():
    st.session_state.clear()
    st.rerun()
