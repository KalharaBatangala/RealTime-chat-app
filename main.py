from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORS
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json
import asyncio

# Initialize FastAPI
app = FastAPI()

# Enable CORS for Streamlit frontend (running on different port)
app.add_middleware(
    CORS,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Store connected WebSocket clients
connected_clients = []

@app.get("/")
async def root():
    return {"message": "Chat App Backend"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Verify Firebase token
            try:
                decoded_token = auth.verify_id_token(data.get("token"))
                user_id = decoded_token["uid"]
                message = data.get("message")
                # Save message to Firestore
                db.collection("messages").add({
                    "user_id": user_id,
                    "message": message,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
                # Broadcast message to all clients
                for client in connected_clients:
                    await client.send_json({
                        "user_id": user_id,
                        "message": message
                    })
            except Exception as e:
                await websocket.send_json({"error": "Invalid token"})
    except WebSocketDisconnect:
        connected_clients.remove(websocket)