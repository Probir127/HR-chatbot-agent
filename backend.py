from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from vector import retriever 
from tools import calculator
import re

# Setup the model
model = OllamaLLM(
    model="llama3.2",
    temperature=0.1,
    max_tokens=1000,
)

# Simple template that works with both RAG and tools
template = """
You are a helpful HR Chatbot for Acme AI Ltd. Use the context below to answer questions accurately.

CONTEXT FROM HR POLICIES:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. If the question can be answered from the context above, provide the answer directly
2. If the question requires a calculation (salary, percentages, math), use the calculator tool
3. For calculations, respond with: CALCULATOR: [expression]
   Examples: 
   - "CALCULATOR: 50000 * 0.3125"
   - "CALCULATOR: 16 / 4"
   - "CALCULATOR: 1800 * 5"
4. Be friendly and helpful in your responses

RESPONSE:
"""

prompt = ChatPromptTemplate.from_template(template)

def ask_hr_bot(question: str, chat_history=None, session_id=None) -> str:
    """
    Simple HR bot that uses RAG for knowledge and calculator for math
    """
    try:
        # 1. Get relevant context from knowledge base
        retrieved_docs = retriever.invoke(question)
        context_text = "\n---\n".join([doc.page_content for doc in retrieved_docs])
        
        # 2. Get bot's initial response
        response = model.invoke(prompt.format(
            question=question, 
            context=context_text
        ))
        
        # 3. Check if calculator is needed
        if "CALCULATOR:" in response:
            # Extract the calculation expression
            match = re.search(r"CALCULATOR:\s*(.+)", response)
            if match:
                expression = match.group(1).strip()
                print(f"🔢 Calculating: {expression}")
                
                # Use the calculator tool
                calc_result = calculator.invoke({"expression": expression})
                
                # Return the calculation result
                return calc_result
        
        # 4. Return direct answer from context
        return response
        
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."

# For API compatibility
def ask_hr_bot_api(question: str, chat_history=None, session_id=None) -> str:
    return ask_hr_bot(question, chat_history, session_id)

# Test the bot
if __name__ == "__main__":
    print("🤖 HR Chatbot Ready! (RAG + Calculator)")
    print("Ask about HR policies or calculations...\n")
    
    while True:
        question = input("You: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        if not question:
            continue
            
        answer = ask_hr_bot(question)
        print(f"HR Bot: {answer}\n")