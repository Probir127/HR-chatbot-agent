"""
backend.py - Optimized HR Chatbot with Modern LangChain Memory (LCEL)
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from vector import retriever 
from tools import calculator, context_awareness_filter
import re
from typing import List, Dict, Optional

# Setup the model
model = OllamaLLM(
    model="llama3.2"
)

class ConversationContextManager:
    """Manages conversation context intelligently"""
    
    @staticmethod
    def has_reference(question: str) -> bool:
        """Check if question has pronouns or references"""
        refs = ['he', 'his', 'him', 'she', 'her', 'it', 'its', 'that', 'this', 'them', 'their']
        question_words = question.lower().split()
        return any(ref in question_words for ref in refs)
    
    @staticmethod
    def is_greeting(question: str) -> bool:
        """Check if the input is a greeting"""
        question_lower = question.lower().strip()
        
        # Remove punctuation for checking
        question_clean = re.sub(r'[^\w\s]', '', question_lower)
        
        # Common greetings
        greetings = [
            'hello', 'hi', 'hey', 'greetings', 'good morning', 
            'good afternoon', 'good evening', 'hi there', 'hey there',
            'hello there', 'sup', 'whats up', 'yo', 'hiya', 'howdy',
            'good day', 'salaam', 'assalam', 'salam'
        ]
        
        # Check if it's a short phrase that's just a greeting
        words = question_clean.split()
        
        # If 4 words or less and contains greeting, it's a greeting
        if len(words) <= 4:
            for greeting in greetings:
                if greeting in question_lower or question_lower.startswith(greeting):
                    return True
        
        return False


# ENHANCED OPTIMIZED PROMPT WITH MEMORY PLACEHOLDER
optimized_prompt_template = """You are the official HR Assistant for Acme AI Ltd., designed to provide accurate, helpful, and professional support to employees.

KNOWLEDGE BASE (HR Policies, Employee Data, Procedures):
{context}

CURRENT EMPLOYEE QUERY: {question}


YOUR CORE RESPONSIBILITIES:

1. ACCURACY & TRUST
   - Answer EXCLUSIVELY from the knowledge base provided above
   - If information is unavailable or unclear, respond with:
     "I don't have that specific information in my current knowledge base. 
      Please contact HR at people@acmeai.tech or call +8801313094329 for accurate details."
   - NEVER fabricate, guess, or assume information
   - When uncertain, always defer to HR department

2. CONTEXT INTELLIGENCE
   - Track pronouns (he/she/his/her/it/that/this/they/their) and resolve them using conversation history
   - Maintain conversation continuity - reference previous exchanges naturally
   - Remember subjects being discussed across multiple questions
   - If context is ambiguous, ask for clarification rather than guessing

3. COMMUNICATION STYLE
   - Be direct and professional - NO greetings in follow-up responses
   - Use clear, workplace-appropriate language
   - Structure complex information with bullets or numbered lists
   - Keep responses concise but complete - avoid unnecessary verbosity
   - Use empathetic tone while maintaining professionalism

4. CALCULATIONS & NUMBERS
   - For ALL mathematical operations, use: CALCULATOR: [expression]
   
   Examples:
   * Salary calculation: CALCULATOR: 40000 * 0.3125
   * Leave division: CALCULATOR: 16 / 4
   * Deduction: CALCULATOR: 1800 * 5
   * Percentage: CALCULATOR: 50000 * 0.5
   
   - Never calculate manually - always use CALCULATOR format
   - Explain what the calculation represents in context

5. SPECIALIZED QUERY HANDLING

   A. "WHO IS..." QUESTIONS:
   - Search: Employee database + Management contacts + Job roles
   - Provide: Full name | Position/Title | Email | Table | Additional context
   - Format: "The [Position] is [Full Name], who [additional role/info]. 
             You can reach them at [email]."
   - Example: "Who is the COO?" 
     Answer: "The COO (Chief Operating Officer) is Syed Sadhli Ahmed Roomy, 
             who is also the Co-Founder of Acme AI Ltd. For operations matters, 
             contact partnership@acmeai.tech"

   B. EMPLOYEE INFORMATION:
   - Include: Name, Position, Email, Table, Blood Group, Team
   - For team queries: List all members with complete details
   - For hierarchy queries: Show reporting structure clearly

   C. POLICY QUESTIONS:
   - Explain thoroughly with specific details
   - Include: Eligibility criteria, timeframes, procedures, exceptions
   - Cite specific numbers, percentages, and deadlines
   - Add: "For clarification, contact HR at people@acmeai.tech"

   D. CONTACT REQUESTS:
   - Always provide: Email + Phone number (if available)
   - Key contacts:
     * HR: people@acmeai.tech | +8801313094329
     * Operations: project@acmeai.tech
     * IT: it.team@acmetechltd.com

   E. PROCEDURE QUESTIONS:
   - Format as numbered steps:
     1. [Action] - [Who to contact]
     2. [Next action] - [Required documents]
     3. [Final step] - [Expected timeline]
   - Include prerequisites and requirements
   - Mention consequences of missing deadlines

6. QUALITY STANDARDS
   - Maintain strict confidentiality
   - Be impartial and fair to all employees
   - Respect cultural and personal sensitivities
   - For critical matters (termination, legal, sensitive), advise consulting HR directly
   - If query is outside HR scope, acknowledge and suggest appropriate department


PROVIDE YOUR ANSWER NOW (Direct, No Greeting):
"""

# Create prompt with memory placeholder - Modern LCEL approach
prompt = ChatPromptTemplate.from_messages([
    ("system", optimized_prompt_template),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])


class InMemoryHistory:
    """Simple in-memory chat history store"""
    
    def __init__(self):
        self.store = {}
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = ChatMessageHistory()
        return self.store[session_id]
    
    def clear_session(self, session_id: str):
        if session_id in self.store:
            self.store[session_id].clear()


class HRChatbot:
    """Optimized HR Chatbot with Modern LangChain Memory (LCEL)"""
    
    def __init__(self):
        self.context_mgr = ConversationContextManager()
        self.model = model
        self.retriever = retriever
        
        # Modern memory store
        self.history_store = InMemoryHistory()
        
        # Create the base chain using LCEL (modern approach)
        self.base_chain = prompt | self.model | StrOutputParser()
    
    def clear_session_memory(self, session_id: str):
        """Clear memory for a specific session"""
        self.history_store.clear_session(session_id)
    
    def answer(self, question: str, session_id: str = "default") -> str:
        """Generate contextually aware answer with memory"""
        try:
            question_stripped = question.strip()
            
            # Get session history
            history = self.history_store.get_session_history(session_id)
            
            # DIRECT GREETING HANDLER - Bypass LLM entirely for greetings
            if self.context_mgr.is_greeting(question_stripped):
                chat_messages = history.messages
                
                if len(chat_messages) == 0:
                    response = "Hello! I'm the HR Chatbot for Acme AI Ltd. How can I help you with HR-related questions today?"
                else:
                    response = "Hello! How can I assist you?"
                
                # Manually add to history
                history.add_user_message(question_stripped)
                history.add_ai_message(response)
                
                return response
            
            # Get relevant documents
            retrieved_docs = self.retriever.invoke(question_stripped)
            context_text = "\n---\n".join([doc.page_content for doc in retrieved_docs])
            
            # Get chat history for the prompt
            chat_messages = history.messages
            
            # Invoke base chain directly with chat history
            response = self.base_chain.invoke({
                "context": context_text[:3000],
                "question": question_stripped,
                "chat_history": chat_messages
            })
            
            # Manually add to history
            history.add_user_message(question_stripped)
            history.add_ai_message(response)
            
            # Clean response
            cleaned = context_awareness_filter.invoke({"response": response})
            cleaned = self._clean_followup(cleaned)
            cleaned = self._handle_calc(cleaned, question_stripped)
            
            # Final validation
            if not cleaned or len(cleaned.strip()) < 5:
                return "I apologize, but I couldn't generate a proper response. Could you please rephrase your question?"
            
            return cleaned.strip()
            
        except Exception as e:
            print(f"Error in answer(): {str(e)}")
            import traceback
            traceback.print_exc()
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    def _clean_followup(self, text: str) -> str:
        """Remove ALL greetings from responses"""
        patterns = [
            r'^Hello!.*?(?:\n|\.)',
            r'^Hi!.*?(?:\n|\.)',
            r'^Good morning.*?(?:\n|\.)',
            r'^Good afternoon.*?(?:\n|\.)',
            r'^Good evening.*?(?:\n|\.)',
            r"^I'm the HR Chatbot for Acme AI Ltd\.\s*",
            r"^How can I help you.*?\?\s*",
            r"^How can I assist you.*?\?\s*",
            r"^I'd be happy to help.*?\.\s*",
            r"^I see that you're.*?\.\s*",
        ]
        
        original = text
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL | re.MULTILINE)
        
        if text != original:
            text = text.lstrip()
        
        return text.strip()
    
    def _handle_calc(self, text: str, question: str) -> str:
        """Handle calculations"""
        if "CALCULATOR:" not in text:
            return text
        
        match = re.search(r"CALCULATOR:\s*(.+)", text)
        if not match:
            return text
        
        expression = match.group(1).strip()
        
        # Skip for policy questions
        skip_words = ['policy', 'sick', 'leave', 'paid']
        if any(w in question.lower() for w in skip_words):
            return text.replace("CALCULATOR:", "").strip()
        
        # Calculate
        calc_result = calculator.invoke({"expression": expression})
        return calc_result


# Global instance
hr_chatbot = HRChatbot()

def ask_hr_bot(question: str, chat_history: Optional[List[Dict]] = None, session_id: Optional[str] = None) -> str:
    """Main function - now uses session_id for memory"""
    if session_id is None:
        session_id = "default"
    
    return hr_chatbot.answer(question, session_id)

def ask_hr_bot_api(question: str, chat_history: Optional[List[Dict]] = None, session_id: Optional[str] = None) -> str:
    """API wrapper - uses session_id for memory management"""
    if session_id is None:
        session_id = "default"
    
    return ask_hr_bot(question, chat_history, session_id)

def clear_session(session_id: str = "default"):
    """Clear memory for a specific session"""
    hr_chatbot.clear_session_memory(session_id)


if __name__ == "__main__":
    print("🤖 HR Chatbot with Modern LangChain Memory (LCEL)")
    print("Commands: 'clear' | 'quit'\n")
    
    session_id = "test_session"
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            if question.lower() == 'clear':
                clear_session(session_id)
                print("✓ Memory cleared")
                continue
            
            # Get answer (memory is handled internally)
            answer = ask_hr_bot(question, session_id=session_id)
            print(f"\nBot: {answer}")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
