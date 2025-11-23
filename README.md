# HR Chatbot (Local RAG + Authentication)


## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/probir127/hr-chatbot.git
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
uvicorn api_server:app --reload
```

---

## Usage

### Run Chatbot in CLI Mode
```bash
python backend.py
```

---

