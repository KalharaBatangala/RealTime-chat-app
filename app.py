import streamlit as st
from streamlit_javascript import st_javascript
import json
import websocket
import threading

# Streamlit page config
st.set_page_config(page_title="Real-Time Chat App", layout="wide")

# Firebase Authentication (client-side JavaScript)
st.markdown("""
<script src="https://www.gstatic.com/firebasejs/9.6.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.6.0/firebase-auth.js"></script>
<script>
    const firebaseConfig = {
        apiKey: "AIzaSyDcSWTrvcHQ6s6XQSC99qM848N96jX3CdQ",
        authDomain: "chat-app-a765a.firebaseapp.com",
        projectId: "chat-app-a765a",
        storageBucket: "chat-app-a765a.firebasestorage.app",
        messagingSenderId: "962580258120",
        appId: "1:962580258120:web:3fc77bbf9efc3b307b677d"
    };
    firebase.initializeApp(firebaseConfig);
</script>
""", unsafe_allow_html=True)

# Replace placeholders with your Firebase config (from Firebase Console > Project Settings > General > Your apps > Web app)

# Session state for user and messages
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Get Firebase token
def get_firebase_token():
    js_code = """
    new Promise((resolve) => {
        firebase.auth().onAuthStateChanged((user) => {
            if (user) {
                user.getIdToken().then((token) => {
                    resolve(token);
                });
            } else {
                resolve(null);
            }
        });
    });
    """
    return st_javascript(js_code)

# WebSocket connection
def connect_websocket(token):
    ws = websocket.WebSocketApp(
        "ws://localhost:8000/ws",
        on_message=lambda ws, msg: on_message(ws, msg),
        on_error=lambda ws, err: st.error(f"WebSocket error: {err}"),
        on_close=lambda ws, code, reason: st.warning("WebSocket closed")
    )
    ws.on_open = lambda ws: ws.send(json.dumps({"token": token, "message": ""}))
    threading.Thread(target=ws.run_forever, daemon=True).start()
    return ws

def on_message(ws, message):
    data = json.loads(message)
    if "error" not in data:
        st.session_state.messages.append(f"{data['user_id']}: {data['message']}")
        st.experimental_rerun()

# Main app
st.title("Real-Time Chat App")

if not st.session_state.user:
    st.subheader("Sign In")
    st.markdown("""
    <button onclick="firebase.auth().signInWithEmailAndPassword(
        document.getElementById('email').value,
        document.getElementById('password').value
    ).then(() => {window.location.reload();}).catch((error) => {alert(error.message);})">
        Sign In
    </button>
    <input type="email" id="email" placeholder="Email">
    <input type="password" id="password" placeholder="Password">
    <br>
    <button onclick="firebase.auth().createUserWithEmailAndPassword(
        document.getElementById('email').value,
        document.getElementById('password').value
    ).then(() => {window.location.reload();}).catch((error) => {alert(error.message);})">
        Sign Up
    </button>
    """, unsafe_allow_html=True)
else:
    st.subheader(f"Welcome, {st.session_state.user}")
    st.button("Sign Out", on_click=lambda: firebase_sign_out())

    # Chat interface
    message = st.text_input("Your message")
    if st.button("Send"):
        if message:
            ws.send(json.dumps({"token": st.session_state.token, "message": message}))

    # Display messages
    for msg in st.session_state.messages:
        st.write(msg)

# Handle authentication
token = get_firebase_token()
if token:
    st.session_state.token = token
    st.session_state.user = "User"  # Replace with actual user data if needed
    ws = connect_websocket(token)

def firebase_sign_out():
    st_javascript("firebase.auth().signOut().then(() => {window.location.reload();})")
    st.session_state.user = None
    st.session_state.token = None
    st.session_state.messages = []