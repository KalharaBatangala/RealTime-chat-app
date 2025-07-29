from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, auth, firestore
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://localhost:8501"],
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

class Message(BaseModel):
    token: str
    message: str

@app.get("/")
async def root():
    return {"message": "Chat App Backend"}

@app.post("/send_message")
async def send_message(msg: Message):
    try:
        decoded_token = auth.verify_id_token(msg.token)
        user_id = decoded_token["uid"]
        message = msg.message
        doc_ref = db.collection("messages").add({
            "user_id": user_id,
            "message": message,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        doc = db.collection("messages").document(doc_ref[1].id).get()
        timestamp = doc.to_dict().get("timestamp").strftime("%Y-%m-%d %H:%M:%S")
        print(f"Sending message: {user_id}: {message} at {timestamp}")
        # Broadcast to WebSocket clients (if any)
        for client in connected_clients:
            try:
                await client.send_json({
                    "user_id": user_id,
                    "message": message,
                    "timestamp": timestamp
                })
            except Exception as e:
                print(f"Error sending to client: {str(e)}")
        return {"status": "Message sent"}
    except Exception as e:
        return {"error": f"Invalid token or error: {str(e)}"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print(f"WebSocket connected: {len(connected_clients)} clients")
    try:
        while True:
            data = await websocket.receive_json()
            print(f"Received data: {data}")
            if data.get("ping") == "keep-alive":
                await websocket.send_json({"pong": "keep-alive"})
                continue
            try:
                decoded_token = auth.verify_id_token(data.get("token"))
                user_id = decoded_token["uid"]
                message = data.get("message")
                if message:
                    doc_ref = db.collection("messages").add({
                        "user_id": user_id,
                        "message": message,
                        "timestamp": firestore.SERVER_TIMESTAMP
                    })
                    doc = db.collection("messages").document(doc_ref[1].id).get()
                    timestamp = doc.to_dict().get("timestamp").strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Sending message: {user_id}: {message} at {timestamp}")
                    for client in connected_clients:
                        try:
                            await client.send_json({
                                "user_id": user_id,
                                "message": message,
                                "timestamp": timestamp
                            })
                        except Exception as e:
                            print(f"Error sending to client: {str(e)}")
            except Exception as e:
                error_msg = f"Invalid token: {str(e)}"
                print(error_msg)
                await websocket.send_json({"error": error_msg})
    except WebSocketDisconnect as e:
        connected_clients.remove(websocket)
        print(f"WebSocket disconnected: {len(connected_clients)} clients, reason: {str(e)}")