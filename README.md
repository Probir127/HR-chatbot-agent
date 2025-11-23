# HR Chatbot - Acme AI Ltd.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.2.16-2C3E50.svg?style=flat)](https://www.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4.24-FF6F61.svg?style=flat)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> An intelligent, context-aware HR chatbot powered by AI for Acme AI Ltd. Built with FastAPI, LangChain, and Ollama LLM for seamless employee support and HR query resolution.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Database Schema](#-database-schema)
- [Deployment](#-deployment)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 🤖 **Intelligent Chatbot**
- **Context-Aware Responses**: Remembers conversation history and maintains context  
- **Natural Language Processing**: Powered by Llama 3.2 via Ollama  
- **Smart Greeting Detection**: Handles greetings without invoking LLM  
- **Pronoun Resolution**: Understands references like "he", "she", "his", "it"  
- **Built-in Calculator**: Performs salary and leave calculations  

### 🔐 **Authentication & Security**
- **JWT-Based Authentication**  
- **Password Hashing (bcrypt)**  
- **Protected Endpoints**  
- **Session Management**  

### 📚 **Knowledge Base**
- **ChromaDB Vector Search**  
- **Multi-Source Data**: PDFs, JSON employee DB, Policies  
- **Top-K Document Retrieval**  

### 💼 **HR Capabilities**
- Employee lookup  
- Salary calculation  
- Leave policy  
- HR policies  
- Job roles  
- Onboarding support  

---

## 🏗️ Architecture

┌─────────────────┐
│ Flutter App │ ← Mobile/Web Frontend
└────────┬────────┘
│ HTTP/REST
▼
┌─────────────────┐
│ FastAPI API │ ← Authentication & Routing
└────────┬────────┘
│
▼
┌─────────────────┐
│ Backend Core │ ← LangChain + Ollama LLM
└────────┬────────┘
│
┌────┴────┐
▼ ▼
┌────────┐ ┌──────────┐
│ChromaDB│ │ JSON DB │
│Vector │ │ Users & │
│Store │ │ Ratings │
└────────┘ └──────────┘

yaml
Copy code

### **Tech Stack**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | FastAPI | REST API |
| AI Layer | LangChain | LLM orchestration |
| LLM | Ollama (Llama 3.2) | Reasoning |
| DB | ChromaDB | Vector search |
| Embeddings | mxbai-embed-large | Semantic embeddings |
| Auth | JWT + bcrypt | Secure login |
| Frontend | Flutter | Mobile/Web |

---

## 📦 Prerequisites

### Required Software
- Python 3.11+  
- Ollama  
- Git  

### Ollama Models

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
System Requirements
8GB RAM minimum

Windows/Linux/macOS

🚀 Installation
1. Clone
bash
Copy code
git clone https://github.com/your-org/hr-chatbot.git
cd hr-chatbot
2. Virtual Environment
bash
Copy code
python -m venv venv
venv\Scripts\activate
3. Install Requirements
bash
Copy code
pip install -r requirements.txt
4. Environment Variables
Create .env:

env
Copy code
SECRET_KEY=your-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CHROMA_DB_PATH=./chroma_hr_db
USERS_FILE=users.json
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
OLLAMA_EMBEDDING_MODEL=mxbai-embed-large
5. Build Vector Database
bash
Copy code
python vector.py
6. Start Server
bash
Copy code
uvicorn api_server:app --reload
💻 Usage
CLI Mode
bash
Copy code
python backend.py
API Examples
Register
bash
Copy code
curl -X POST http://127.0.0.1:8000/auth/register ...
Login
bash
Copy code
curl -X POST http://127.0.0.1:8000/auth/login ...
Chat
bash
Copy code
curl -X POST http://127.0.0.1:8000/chat ...
📖 API Documentation
Swagger UI → http://127.0.0.1:8000/docs

ReDoc → http://127.0.0.1:8000/redoc

Endpoints Overview
Method	Endpoint	Auth	Description
GET	/	No	Health
POST	/auth/register	No	Register
POST	/auth/login	No	Login
GET	/auth/me	Yes	Current user
POST	/chat	Yes	Send message
POST	/new-session	Yes	New session
POST	/rate	Yes	Rate response

📜 License
MIT License.

yaml
Copy code

---

If you want this turned into a **README.md file**, just say **"create README.md"** and I will generate
