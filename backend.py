"""
backend.py - Optimized HR Chatbot with Dynamic Top-K Retrieval
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from vector import retriever, get_dynamic_retriever
from tools import calculator, context_awareness_filter
import re
from typing import List, Dict, Optional

# Setup the model with lower temperature for maximum accuracy and reduced hallucination
model = OllamaLLM(
    model="llama3.2",
    temperature=0.0,  # Set to 0 for deterministic, factual responses
    max_tokens=1000,
)

class ConversationContextManager:
    """Manages conversation context intelligently"""
    
    @staticmethod
    def format_history(chat_history: List[Dict], max_exchanges: int = 3) -> str:
        """Format recent conversation history"""
        if not chat_history:
            return ""
        
        recent = chat_history[-max_exchanges:]
        lines = ["RECENT CONVERSATION:"]
        
        for i, exchange in enumerate(recent, 1):
            lines.append(f"{i}. User: {exchange.get('user', '')}")
            lines.append(f"   Bot: {exchange.get('bot', '')[:150]}...")
        
        return "\n".join(lines)
    
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
        question_clean = re.sub(r'[^\w\s]', '', question_lower)
        
        greetings = [
            'hello', 'hi', 'hey', 'greetings', 'good morning', 
            'good afternoon', 'good evening', 'hi there', 'hey there',
            'hello there', 'sup', 'whats up', 'yo', 'hiya', 'howdy',
            'good day', 'salaam', 'assalam', 'salam'
        ]
        
        words = question_clean.split()
        
        if len(words) <= 4:
            for greeting in greetings:
                if greeting in question_lower or question_lower.startswith(greeting):
                    return True
        
        return False
    
    @staticmethod
    def classify_query_complexity(question: str) -> str:
        """
        Classify query complexity for optimal retrieval.
        
        Returns: 'simple', 'employee_lookup', 'calculation', 'greeting', 'complex'
        """
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        
        if any(word in question_lower for word in ['who is', 'who are', 'find employee', 'contact', 'email']):
            return 'employee_lookup'
        
        if any(word in question_lower for word in ['calculate', 'salary', 'breakdown', 'basic salary']):
            return 'calculation'
        
        # Check for complex queries
        if len(question.split()) > 15 or ('?' in question and question.count('?') > 1):
            return 'complex'
        
        return 'simple'


# ENHANCED OPTIMIZED PROMPT with added emphasis on accuracy and no hallucination
optimized_prompt = """You are the official HR Assistant for Acme AI Ltd., designed to provide accurate, helpful, and professional support to employees.

===============================================================================
CONVERSATION CONTEXT:
{history}

KNOWLEDGE BASE (HR Policies, Employee Data, Procedures):
{context}

CURRENT EMPLOYEE QUERY: {question}
===============================================================================

YOUR CORE RESPONSIBILITIES:

1. ACCURACY & TRUST (CRITICAL - NO HALLUCINATION ALLOWED)
   - Answer EXCLUSIVELY from the knowledge base provided above. Do NOT use external knowledge, assumptions, or generalizations.
   - If information is unavailable or unclear in the knowledge base, respond EXACTLY with:
     "I don't have that specific information in my current knowledge base. 
      Please contact HR at people@acmeai.tech or call +8801313094329 for accurate details."
   - If question is who made you or created , respond with:
     "my creator is probir saha shohom an intern "
   - NEVER fabricate, guess, assume, hallucinate, or invent any information, names, policies, or details.
   - When uncertain or if the query cannot be answered from the provided context, always defer to HR department without adding any extra information.
   - Double-check your response: Ensure every fact, name, number, and detail is directly supported by the knowledge base. If not, use the deferral message.

2. CONTEXT INTELLIGENCE
   - Track pronouns (he/she/his/her/it/that/this/they/their) and resolve them using CONVERSATION CONTEXT
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
   - Format as numbered steps with clear actions
   - Include prerequisites and requirements
   - Mention consequences of missing deadlines

6. QUALITY STANDARDS
   - Maintain strict confidentiality
   - Be impartial and fair to all employees
   - Respect cultural and personal sensitivities
   - For critical matters (termination, legal, sensitive), advise consulting HR directly
   - If query is outside HR scope, acknowledge and suggest appropriate department

===============================================================================
PROVIDE YOUR ANSWER NOW (Direct, No Greeting, Strictly from Context):
"""

prompt = ChatPromptTemplate.from_template(optimized_prompt)

class HRChatbot:
    """Optimized HR Chatbot with Dynamic Top-K Retrieval"""
    
    def __init__(self):
        self.context_mgr = ConversationContextManager()
        self.model = model
        self.retriever = retriever
    
    def answer(self, question: str, chat_history: Optional[List[Dict]] = None) -> str:
        """Generate contextually aware answer with optimized retrieval"""
        try:
            chat_history = chat_history or []
            question_stripped = question.strip()
            
            # DIRECT GREETING HANDLER
            if self.context_mgr.is_greeting(question_stripped):
                if len(chat_history) == 0:
                    return "Hello! I'm the HR Chatbot for Acme AI Ltd. How can I help you with HR-related questions today?"
                else:
                    return "Hello! How can I assist you?"
            
            # DIRECT ANSWER FOR EXECUTIVE QUERIES - FIX FOR COO QUESTION
            question_lower = question_stripped.lower()
            
            # Handle COO queries
            if any(term in question_lower for term in ['coo', 'chief operating officer', 'sadhli']):
                return "The Chief Operating Officer (COO) and Co-Founder of Acme AI Ltd. is Syed Sadhli Ahmed Roomy."
            
            # Handle Chairman queries
            if any(term in question_lower for term in ['chairman', 'fatemy']):
                return "The Chairman of Acme AI Ltd. is Major Gen Syed Fatemy Ahmed Roomy (Retd)."
            
            # Handle Founder queries
            if any(term in question_lower for term in ['founder', 'founded', 'sharek']):
                return "Acme AI Ltd. was founded in 2020 by Syed Sharek Ahmed Roomy and co-founded by Syed Sadhli Ahmed Roomy."
            
            # Handle "who made you" queries
            if any(term in question_lower for term in ['who made you', 'who created you', 'creator']):
                return "My creator is Probir Saha Shohom, an intern."
            
            # Classify query complexity
            query_type = self.context_mgr.classify_query_complexity(question)
            
            # Format history only if question has references
            if self.context_mgr.has_reference(question):
                history_text = self.context_mgr.format_history(chat_history)
            else:
                history_text = ""
            
            # Get retriever with optimal k based on query type
            dynamic_retriever = get_dynamic_retriever(question)
            
            # Get relevant documents with optimized k
            retrieved_docs = dynamic_retriever.invoke(question)
            
            # Limit context to prevent overwhelming the model
            context_limit = {
                'greeting': 500,
                'employee_lookup': 1500,
                'calculation': 1000,
                'simple': 2500,
                'complex': 3500
            }.get(query_type, 2500)
            
            context_text = "\n---\n".join([doc.page_content for doc in retrieved_docs])
            context_text = context_text[:context_limit]
            
            # Build prompt
            full_prompt = prompt.format(
                history=history_text,
                context=context_text,
                question=question
            )
            
            # Get response
            response = self.model.invoke(full_prompt)
            
            # Clean response
            cleaned = context_awareness_filter.invoke({"response": response})
            cleaned = self._clean_followup(cleaned)
            
            # Handle calculations
            cleaned = self._handle_calc(cleaned, question)
            
            # Additional accuracy check: If response doesn't seem grounded, defer
            if not self._is_response_grounded(cleaned, context_text, question):
                return "I don't have that specific information in my current knowledge base. Please contact HR at people@acmeai.tech or call +8801313094329 for accurate details."
            
            # Final validation
            if not cleaned or len(cleaned.strip()) < 5:
                return "I apologize, but I couldn't generate a proper response. Could you please rephrase your question?"
            
            return cleaned.strip()
            
        except Exception as e:
            print(f"Error in answer(): {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    def _is_response_grounded(self, response: str, context: str, question: str) -> bool:
        """Basic check to ensure response is grounded in context (simple heuristic)"""
        # Skip for greetings or very short responses
        if len(response.strip()) < 20 or self.context_mgr.is_greeting(question):
            return True
        
        # Check if key entities in response appear in context (basic check)
        response_lower = response.lower()
        context_lower = context.lower()
        
        # Extract potential key phrases (names, emails, etc.)
        key_phrases = re.findall(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b|\b\w+@\w+\.\w+\b|\b\d{10,}\b', response)
        if not key_phrases:
            return True  # No specific entities, assume ok
        
        # Check if at least one key phrase is in context
        for phrase in key_phrases:
            if phrase.lower() in context_lower:
                return True
        
        return False  # If no grounding found, likely hallucinated
    
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
    """Main function"""
    return hr_chatbot.answer(question, chat_history)

def ask_hr_bot_api(question: str, chat_history: Optional[List[Dict]] = None, session_id: Optional[str] = None) -> str:
    """API wrapper"""
    return ask_hr_bot(question, chat_history, session_id)


if __name__ == "__main__":
    print(" HR Chatbot with Optimized Dynamic Top-K Retrieval")
    print("Commands: 'clear' | 'quit'\n")
    
    chat_history = []
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if question.lower() == 'clear':
                chat_history = []
                print("✓ History cleared")
                continue
            
            # Get answer
            answer = ask_hr_bot(question, chat_history)
            print(f"\nBot: {answer}")
            
            # Update history
            chat_history.append({"user": question, "bot": answer})
            
            # Keep last 10
            if len(chat_history) > 10:
                chat_history = chat_history[-10:]
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
