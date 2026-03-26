import urllib.parse
import requests
import streamlit as st

def get_google_login_url(client_id, redirect_uri):
    auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
    }
    return f"{auth_url}?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(code, client_id, client_secret, redirect_uri):
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    response = requests.post(token_url, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        # Return error details instead of None
        return {"error": response.status_code, "details": response.text}

def get_user_info(access_token):
    user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(user_info_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def verify_google_oauth():
    """ Returns user dict if authenticated, else None """
    if "user_email" in st.session_state:
        return {"email": st.session_state.user_email, "name": st.session_state.get("user_name", "")}

    try:
        client_id = st.secrets["GOOGLE_CLIENT_ID"]
        client_secret = st.secrets["GOOGLE_CLIENT_SECRET"]
        redirect_uri = st.secrets["REDIRECT_URI"]
    except KeyError as e:
        st.error(f"Missing secret: {e}. Please add it to .streamlit/secrets.toml")
        return None

    # Handle OAuth callback - Google sends ?code=... back to our redirect_uri
    query_params = st.query_params

    if "code" in query_params:
        code = query_params["code"]
        st.query_params.clear()

        token_data = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
        if token_data and "access_token" in token_data:
            user_info = get_user_info(token_data["access_token"])
            if user_info and "email" in user_info:
                st.session_state.user_email = user_info["email"]
                st.session_state.user_name = user_info.get("name", "User")
                st.rerun()
        else:
            if token_data:
                st.error(f"❌ Token exchange failed (HTTP {token_data.get('error')})\n\n**Details:**\n{token_data.get('details', 'Unknown error')}")
            else:
                st.error("Token exchange failed: No response from Google")

    st.title("Welcome to Daylytics 📈")
    st.write("Please sign in to manage your tasks securely.")

    login_url = get_google_login_url(client_id, redirect_uri)

    # Debug - show the exact redirect_uri being used (remove after confirming login works)
    st.caption(f"🔍 Debug — Redirect URI: `{redirect_uri}`")

    st.markdown(
        f'<a href="{login_url}" target="_self">'
        f'<button style="background-color: #4285F4; color: white; padding: 10px 20px; '
        f'border: none; border-radius: 4px; cursor: pointer; font-size: 16px;">'
        f'Sign in with Google</button></a>',
        unsafe_allow_html=True
    )

    return None

def logout():
    st.session_state.clear()
    st.rerun()
