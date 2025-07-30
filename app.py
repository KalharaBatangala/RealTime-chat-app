from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import pyrebase
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secret!")  # Fallback to 'secret!' if not set
socketio = SocketIO(app)

# Firebase configuration from .env
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

@app.route("/")
def index():
    if "user" in session:
        return render_template("chat.html", user=session["user"])
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        session["user"] = user["email"]
        session["token"] = user["idToken"]
        session["refresh_token"] = user["refreshToken"]
        return redirect(url_for("index"))
    except Exception as e:
        return render_template("login.html", error=f"Signin failed: {str(e)}")

@app.route("/signup", methods=["POST"])
def signup():
    email = request.form["email"]
    password = request.form["password"]
    try:
        user = auth.create_user_with_email_and_password(email, password)
        session["user"] = user["email"]
        session["token"] = user["idToken"]
        session["refresh_token"] = user["refreshToken"]
        return redirect(url_for("index"))
    except Exception as e:
        return render_template("login.html", error=f"Signup failed: {str(e)}")

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("token", None)
    session.pop("refresh_token", None)
    return redirect(url_for("index"))

@socketio.on("connect")
def handle_connect():
    if "token" in session:
        emit("status", {"message": "WebSocket connected"})

@socketio.on("message")
def handle_message(data):
    message = data.get("message")
    if message and "token" in session:
        try:
            # Send message to FastAPI backend
            response = requests.post(
                "http://localhost:8000/send_message",
                json={"token": session["token"], "message": message}
            )
            if response.status_code == 200:
                # Emit message to all Socket.IO clients
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                socketio.emit("message", {
                    "user_id": session["user"],
                    "message": message,
                    "timestamp": timestamp
                })
            else:
                emit("error", {"message": f"Failed to send message: {response.text}"})
        except Exception as e:
            emit("error", {"message": f"Failed to send message: {str(e)}"})

@socketio.on("refresh_token")
def refresh_token():
    if "refresh_token" in session:
        try:
            user = auth.refresh(session["refresh_token"])
            session["token"] = user["idToken"]
            session["refresh_token"] = user["refreshToken"]
            emit("status", {"message": "Token refreshed"})
        except Exception as e:
            emit("error", {"message": f"Token refresh failed: {str(e)}"})
            session.pop("user", None)
            session.pop("token", None)
            session.pop("refresh_token", None)

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)