<div align="center">
  <h1>✨ StudyBud: AI-Powered Social Learning Platform</h1>
  <p>A full-stack social learning web application built with Django, Django REST Framework, and Meta's Llama-3 AI via the Groq API. Designed to help students create study rooms, discuss topics, and learn faster using ultra-low latency AI tools.</p>
</div>

<br />

## 🚀 Features

### Core Platform
*   **Study Rooms & Topics:** Users can browse, create, edit, and delete study rooms categorized by topic.
*   **Threaded Discussions:** Deeply nested comment threads with a beautiful, modern UI allowing users to reply directly to specific messages.
*   **Authentication & Profiles:** Full user authentication (Login/Register) and user profiles displaying recent activity.
*   **RESTful API Backend:** All core features are exposed via a robust API built with Django REST Framework (DRF) and secured with JWT authentication (`SimpleJWT`).

### 🧠 AI Integrations (Powered by Groq + Llama 3)
*   **Instant Room Summarization:** Click a button to get a bullet-point summary of the entire chat history in a room, generated in milliseconds.
*   **Smart Reply Suggestions:** Click "AI Suggest" when replying to a comment to instantly generate 3 context-aware, helpful reply suggestions.
*   **Virtual Study Assistant:** A persistent, floating AI chatbot that knows exactly what room and topic you are currently in and can answer questions on the fly.

## 🛠️ Tech Stack

*   **Backend:** Python, Django, Django REST Framework (DRF)
*   **Database:** SQLite (Development), PostgreSQL ready
*   **Frontend:** HTML5, Vanilla CSS (Modern gradients, glassmorphism), Vanilla JavaScript
*   **AI Engine:** [Groq LPU](https://groq.com/) Inference Engine
*   **LLM:** Meta Llama-3.1 (8B Instant)

## 💻 Local Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Set up the Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Note: If `requirements.txt` is missing, you can install the core packages manually: `pip install django djangorestframework djangorestframework-simplejwt groq python-decouple`)*

### 4. Configure Environment Variables
Create a `.env` file in the root directory and add your Groq API key:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000` in your browser.

## 📸 Screenshots
*(Add screenshots of your application here once deployed!)*

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📜 License
This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.
