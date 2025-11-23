# HR Chatbot - Acme AI Ltd.

##  Architecture

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

##  Prerequisites

### Required Software
- Python 3.11+  
- Ollama  
- Git  

### Ollama Models


ollama pull llama3.2
ollama pull mxbai-embed-large
System Requirements
8GB RAM minimum

Windows/Linux/macOS

## Installation
1. Clone
bash
Copy code
git clone https://github.com/your-org/hr-chatbot.git
cd hr-chatbot

3. Virtual Environment
bash
Copy code

python -m venv venv

venv\Scripts\activate

4. Install Requirements
bash
Copy code

pip install -r requirements.txt


ollama pull llama3.2
ollama pull mxbai-embed-large

5. Build Vector Database
bash
Copy code
python vector.py
6. Start Server
bash
Copy code
uvicorn api_server:app --reload


---

