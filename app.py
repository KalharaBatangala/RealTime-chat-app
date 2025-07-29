import streamlit as st
import pyrebase
import json
import websocket
import threading
import time

# Streamlit page config
st.set_page_config(page_title="Real-Time Chat App", layout="wide")

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDcSWTrvcHQ6s6XQSC99qM848N96jX3CdQ",
    "authDomain": "chat-app-a765a.firebaseapp.com",
    "projectId": "chat-app-a765a",
    "storageBucket": "chat-app-a765a.firebasestorage.app",
    "messagingSenderId": "962580258120",
    "appId": "1:962580258120:web:3fc77bbf9efc3b307b677d",
    "databaseURL": ""  # Not needed for Authentication/Firestore
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Session state for user, token, and WebSocket
if "user" not in st.session_state:
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.refresh_token = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ws" not in st.session_state:
    st.session_state.ws = None
if "ws_connected" not in st.session_state:
    st.session_state.ws_connected = False

# WebSocket connection
def connect_websocket(token):
    def on_message(ws, message):
        try:
            data = json.loads(message)
            if "error" not in data:
                sender = st.session_state.user if data['user_id'] == auth.get_account_info(st.session_state.token)['users'][0]['localId'] else data['user_id']
                timestamp = data.get('timestamp', time.strftime("%Y-%m-%d %H:%M:%S"))
                st.session_state.messages.append(f"[{timestamp}] {sender}: {data['message']}")
                st.rerun()
            else:
                st.error(f"WebSocket message error: {data['error']}")
        except Exception as e:
            st.error(f"Error processing message: {str(e)}")

    def on_error(ws, error):
        st.error(f"WebSocket error: {str(error)}")
        st.session_state.ws_connected = False

    def on_close(ws, code, reason):
        st.warning(f"WebSocket closed: {reason or 'No reason provided'} (Code: {code})")
        st.session_state.ws_connected = False

    def on_open(ws):
        ws.send(json.dumps({"token": token, "message": ""}))
        st.session_state.ws_connected = True
        st.success("WebSocket connected")
        # Keep-alive ping
        def keep_alive():
            while st.session_state.ws_connected:
                try:
                    ws.send(json.dumps({"ping": "keep-alive"}))
                    time.sleep(30)  # Ping every 30 seconds
                except:
                    st.session_state.ws_connected = False
                    break
        threading.Thread(target=keep_alive, daemon=True).start()

    ws = websocket.WebSocketApp(
        "ws://localhost:8000/ws",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    threading.Thread(target=ws.run_forever, daemon=True, kwargs={"ping_interval": 30}).start()
    return ws

# Refresh Firebase token
def refresh_token():
    if st.session_state.refresh_token:
        try:
            user = auth.refresh(st.session_state.refresh_token)
            st.session_state.token = user['idToken']
            st.session_state.refresh_token = user['refreshToken']
            return True
        except Exception as e:
            st.error(f"Token refresh failed: {str(e)}")
            return False
    return False

# Main app
st.title("Real-Time Chat App")

# Add CSS for better UI
st.markdown("""
<style>
    .stTextInput > div > input { padding: 10px; margin: 5px; width: 300px; }
    .stButton > button { background-color: #4CAF50; color: white; padding: 10px; margin: 5px; }
    .stButton > button:hover { background-color: #45a049; }
    .chat-message { background-color: #f0f2f6; padding: 10px; margin: 5px 0; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

if not st.session_state.user:
    st.subheader("Sign In / Sign Up")
    
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.user = user["email"]
                st.session_state.token = user["idToken"]
                st.session_state.refresh_token = user["refreshToken"]
                st.session_state.ws = connect_websocket(st.session_state.token)
                st.success(f"Signed in as {user['email']}")
                st.rerun()
            except Exception as e:
                st.error(f"Signin failed: {str(e)}")
    
    with col2:
        if st.button("Sign Up"):
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.session_state.user = user["email"]
                st.session_state.token = user["idToken"]
                st.session_state.refresh_token = user["refreshToken"]
                st.session_state.ws = connect_websocket(st.session_state.token)
                st.success(f"Account created for {user['email']}")
                st.rerun()
            except Exception as e:
                st.error(f"Signup failed: {str(e)}")

else:
    st.subheader(f"Welcome, {st.session_state.user}")
    if st.button("Sign Out"):
        if st.session_state.ws:
            try:
                st.session_state.ws.close()
            except:
                pass
        st.session_state.user = None
        st.session_state.token = None
        st.session_state.refresh_token = None
        st.session_state.ws = None
        st.session_state.ws_connected = False
        st.session_state.messages = []
        st.rerun()

    # Refresh token if expired
    if st.session_state.user and st.session_state.token:
        if not refresh_token():
            st.error("Session expired. Please sign in again.")
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.refresh_token = None
            st.session_state.ws = None
            st.session_state.ws_connected = False
            st.rerun()

    # Check and reconnect WebSocket if closed
    if st.session_state.user and st.session_state.token and (not st.session_state.ws or not st.session_state.ws_connected):
        try:
            if st.session_state.ws:
                st.session_state.ws.close()
        except:
            pass
        st.session_state.ws = connect_websocket(st.session_state.token)

    # Chat interface
    message = st.text_input("Your message")
    if st.button("Send"):
        if message:
            if st.session_state.ws and st.session_state.ws_connected:
                try:
                    st.session_state.ws.send(json.dumps({"token": st.session_state.token, "message": message}))
                except Exception as e:
                    st.error(f"Failed to send message: {str(e)}")
                    st.session_state.ws_connected = False
                    st.session_state.ws = connect_websocket(st.session_state.token)
            else:
                st.error("WebSocket not connected. Trying to reconnect...")
                st.session_state.ws = connect_websocket(st.session_state.token)

    # Display messages
    for msg in st.session_state.messages:
        st.markdown(f'<div class="chat-message">{msg}</div>', unsafe_allow_html=True)