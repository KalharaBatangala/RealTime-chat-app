# Real-Time Chat Application

A web-based chat application with user authentication and real-time messaging, built to demonstrate full-stack development and DevOps skills. This project showcases my ability to design, troubleshoot, and deploy a modern web app while overcoming real-world challenges.

## Features

- **User Authentication**: Sign up and log in using Firebase Authentication (Email/Password).
- **Real-Time Group Chat**: Send and receive messages instantly across connected users.
- **Message Persistence**: Store chat messages in Firebase Firestore.
- **Deployment**: Deployed on AWS Elastic Beanstalk using Docker for scalability.

## Tech Stack

### Original Version (Main Branch)
- **Backend**: FastAPI (Python) with WebSocket support for real-time messaging.
- **Frontend**: Streamlit (Python) for the user interface.
- **Authentication**: Firebase Authentication for secure user management.
- **Database**: Firebase Firestore for storing chat messages.
- **Deployment**: AWS Elastic Beanstalk, Docker.
- **Version Control**: Git, GitHub.

### New Version (Flask Branch)
- **Backend**: FastAPI (unchanged, with HTTP and WebSocket endpoints).
- **Frontend**: Flask (Python) with Socket.IO for stable real-time communication.
- **Authentication**: Firebase Authentication (unchanged).
- **Database**: Firebase Firestore (unchanged).
- **Deployment**: AWS Elastic Beanstalk, Docker.
- **Version Control**: Git, GitHub (in a new branch, `flask-frontend`).

## Project Journey and Challenges

### Original Plan with Streamlit
The initial goal was to build a real-time chat app using **FastAPI** for the backend and **Streamlit** for the frontend, integrated with **Firebase** for authentication and data storage. The backend used FastAPI’s WebSocket endpoint (`/ws`) to broadcast messages to all connected clients, while Streamlit provided a simple Python-based UI for users to sign up, log in, and chat. The setup was:

- **Backend**: Run with `uvicorn main:app --reload` on `http://localhost:8000`.
- **Frontend**: Run with `streamlit run app.py` on `http://localhost:8501`.
- **Workflow**:
  - Users sign up/log in via Firebase Authentication.
  - The frontend connects to the backend’s WebSocket endpoint (`ws://localhost:8000/ws`) using the `websocket-client` library.
  - Messages are sent to the backend, stored in Firestore, and broadcast to all clients.

### Challenges Faced
The Streamlit version faced significant challenges, which provided valuable learning opportunities:

1. **React #231 Error**:
   - **Issue**: Early attempts to integrate JavaScript for dynamic UI updates triggered errors related to React’s internal handling (Streamlit uses React under the hood). Specifically, Streamlit’s React framework caused issues when we tried to inject custom JavaScript for WebSocket communication.
   - **Impact**: Limited our ability to add dynamic, real-time features without workarounds.
   - **Lesson**: Streamlit’s reliance on React restricts low-level JavaScript customization, making it unsuitable for JavaScript-heavy apps.

2. **Button Click Handling Issue**:
   - **Issue**: Streamlit sanitizes HTML and doesn’t support inline `onClick` event handlers (e.g., `<button onclick="sendMessage()">`), as React expects JavaScript to be managed through its framework. This caused errors when we tried to add custom JavaScript for sending messages.
   - **Impact**: Forced reliance on Streamlit’s Python-based event handling, which conflicted with WebSocket logic.
   - **Lesson**: Streamlit is designed for Python-driven UIs, not raw HTML/JavaScript, limiting real-time interactivity.

3. **WebSocket Disconnection Errors**:
   - **Issue**: The frontend showed “WebSocket not connected. Trying to reconnect...” errors, and backend logs indicated frequent disconnections (`WebSocket disconnected: 1 clients`).
   - **Cause**: Streamlit reruns the entire `app.py` script on every user interaction (e.g., clicking “Send”), terminating the WebSocket thread (`st.session_state.ws`). This broke the persistent connection needed for real-time messaging.
   - **Lesson**: Streamlit’s reactive model is incompatible with stateful connections like WebSockets.

### Point of Failure
The primary failure was **Streamlit’s rerun behavior**:
- **What Happened**: Streamlit reruns the script on every interaction, resetting or closing the WebSocket connection. This caused the `websocket-client` library to fail, as seen in backend logs (`WebSocket disconnected`) and frontend errors (“WebSocket not connected”).
- **Why Streamlit Wasn’t Suitable**:
  - **Reactive Design**: Streamlit’s reruns are great for data dashboards but disrupt persistent connections like WebSockets.
  - **Limited JavaScript Support**: Streamlit abstracts front-end logic, making it hard to manage real-time updates or custom JavaScript (e.g., for Socket.IO).
  - **Not Built for Real-Time**: Streamlit is optimized for static or slowly updating UIs, not real-time apps like chat.
- **Outcome**: The backend (FastAPI + Firebase) worked correctly, handling authentication and WebSocket messages, but Streamlit’s frontend couldn’t maintain stable connections.

### Transition to Flask + Socket.IO
To address these issues, we pivoted to a **Flask + Socket.IO** frontend in a new branch (`flask-frontend`). Flask is a lightweight Python web framework that:
- Avoids reruns, ensuring stable WebSocket connections.
- Supports HTML templates with JavaScript (Socket.IO) for real-time messaging.
- Integrates seamlessly with the existing FastAPI backend and Firebase.

This version is under development and will be available in the `flask-frontend` branch. It uses:
- **Flask**: Serves HTML templates for login and chat interfaces.
- **Socket.IO**: Handles real-time messaging, replacing the problematic `websocket-client`.
- **FastAPI Backend**: Continues to manage WebSocket broadcasting and Firestore storage.

**Note**: The main branch contains the Streamlit version, which is non-functional due to WebSocket issues. Clone the `flask-frontend` branch for the working version once implemented.

## Setup (Main Branch - Streamlit Version)

**Note**: This version is non-functional due to WebSocket instability. See the `flask-frontend` branch for the working version.

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/KalharaBatangala/RealTime-chat-app.git
   cd RealTime-chat-app
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set Up Firebase**:
   - Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com).
   - Enable **Authentication** (Email/Password) and **Firestore**.
   - Download the service account key as `firebase-adminsdk.json` and place it in `D:\chat-app`.
   - Update `app.py` with your Firebase config (already included for `chat-app-a765a`).

4. **Run the Backend**:
   ```bash
   uvicorn main:app --reload
   ```
   - Access at `http://localhost:8000` (returns `{"message": "Chat App Backend"}`).

5. **Run the Frontend**:
   ```bash
   streamlit run app.py
   ```
   - Access at `http://localhost:8501`.

6. **Expected Issues**:
   - WebSocket connections fail with “WebSocket not connected. Trying to reconnect...” due to Streamlit’s reruns.
   - Messages may not send or display in real-time.

## Setup (Flask-frontend Branch - Working Version)

**Note**: This branch is under development and will contain the stable Flask + Socket.IO version. Instructions are based on the planned implementation.

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/KalharaBatangala/RealTime-chat-app.git
   cd RealTime-chat-app
   git checkout flask-frontend
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set Up Firebase**:
   - Same as above (place `firebase-adminsdk.json` in `D:\chat-app`).

4. **Run the Backend**:
   ```bash
   uvicorn main:app --reload
   ```
   - Access at `http://localhost:8000`.

5. **Run the Frontend**:
   ```bash
   python app.py
   ```
   - Access at `http://localhost:5000`.

6. **Test the App**:
   - Sign up with an email and password.
   - Verify real-time messaging in the chat interface.
   - Open a second tab to test multi-user chat.

## Deployment

### Docker
1. **Build the Docker Image**:
   ```bash
   docker build -t chat-app .
   ```

2. **Run the Container**:
   - For Streamlit (main branch):
     ```bash
     docker run -p 8000:8000 -p 8501:8501 chat-app
     ```
   - For Flask (flask-frontend branch):
     ```bash
     docker run -p 8000:8000 -p 5000:5000 chat-app
     ```

### AWS Elastic Beanstalk
1. **Initialize EB CLI**:
   ```bash
   eb init -p docker chat-app --region us-east-1
   ```

2. **Create Environment**:
   ```bash
   eb create chat-app-env
   ```

3. **Deploy**:
   ```bash
   eb deploy
   ```

4. **Access**:
   - Open the Elastic Beanstalk URL provided by AWS.

## Screenshots

(TODO: Add screenshots of the login page and chat interface once the Flask version is complete.)

## Lessons Learned

This project was a deep dive into real-time web development and DevOps practices:
- **WebSockets vs. HTTP**: Learned that WebSockets enable instant, two-way communication, unlike HTTP’s one-way request-response model.
- **Framework Selection**: Streamlit is great for data dashboards but unsuitable for real-time apps due to its rerun behavior. Flask + Socket.IO is a better fit.
- **Debugging**: Used backend logs to identify WebSocket disconnections and frontend errors to pinpoint Streamlit’s limitations.
- **DevOps Skills**: Gained experience with Docker, AWS Elastic Beanstalk, and GitHub for version control and deployment.

## Future Improvements
- Enhance the Flask UI with user-specific message styling (e.g., different colors for senders).
- Implement private messaging or chat rooms.
- Explore React + FastAPI for a more modern frontend.
- Add CI/CD pipelines with GitHub Actions for automated deployment.

## License

[MIT License](LICENSE)