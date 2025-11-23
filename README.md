# HR Chatbot (Local RAG + Authentication)


## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Probir127/HR-chatbot-agent.git
cd hr-chatbot
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt


ollama pull llama3.2
ollama pull mxbai-embed-large
```

### 5. Build the Vector Database
```bash
python vector.py
```

### 6. Start the FastAPI Server
```bash
uvicorn api_server:app 
```

---

## Host and Port Configuration


To run the HR Chatbot backend on a specific host and port, update your `backend.py` configuration:


```
HOST = "0.0.0.0"
PORT = 8000
```


## Usage

### Run Chatbot in CLI Mode
```bash
python backend.py
```

---

