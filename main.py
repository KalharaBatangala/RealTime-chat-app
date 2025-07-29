from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials, auth, firestore

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
        return {"status": "Message sent"}
    except Exception as e:
        return {"error": f"Invalid token or error: {str(e)}"}