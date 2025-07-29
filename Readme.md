**Real-Time Chat App**
A web-based chat application with user authentication and real-time messaging using FastAPI, Streamlit, Firebase, and AWS.
**Features**

User sign-up and login with Firebase Authentication.
Real-time group chat using WebSockets.
Message storage in Firestore.
Deployed on AWS Elastic Beanstalk with Docker.

**Tech Stack**

Backend: FastAPI, WebSockets
Frontend: Streamlit
Authentication: Firebase Authentication
Database: Firestore
Deployment: AWS Elastic Beanstalk, Docker
Version Control: Git, GitHub

**Setup**

Clone the repository:git clone https://github.com/KalharaBatangala/RealTime-chat-app.git
cd chat-app


Create a virtual environment and install dependencies:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


Set up Firebase:
Create a Firebase project and enable Authentication (Email/Password) and Firestore.
Download the service account key as firebase-adminsdk.json.
Update app.py with your Firebase config.


Run the backend:uvicorn main:app --reload


Run the frontend:streamlit run app.py


Access at http://localhost:8501.

**Deployment**

Build and run with Docker:docker build -t chat-app .
docker run -p 8000:8000 -p 8501:8501 chat-app


Deploy to AWS Elastic Beanstalk:eb init -p docker chat-app --region us-east-1
eb create chat-app-env
eb deploy



**Screenshots**
(Add screenshots of the chat interface and login page here)
License
MIT License