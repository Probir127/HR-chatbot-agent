"""
backend.py - Optimized HR Chatbot with Advanced Context Awareness and Greeting Handler
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from vector import retriever 
from tools import calculator, context_awareness_filter
import re
from typing import List, Dict, Optional

# Setup the model
model = OllamaLLM(
    model="llama3.2",
    temperature=0.1,
    max_tokens=1200,
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


# ENHANCED OPTIMIZED PROMPT
optimized_prompt = """You are the official HR Assistant for Acme AI Ltd. - a professional, knowledgeable, and helpful chatbot.

{history}

RELEVANT HR KNOWLEDGE:
{context}

EMPLOYEE QUESTION: {question}

YOUR ROLE & INSTRUCTIONS:
1. **Accuracy & Reliability**: 
   - Answer ONLY based on the HR knowledge provided above
   - If information is not available, clearly state: "I don't have that specific information. Please contact HR at people@acmeai.tech or call +8801313094329."
   - Never invent or assume information

2. **Context Awareness**:
   - If the question contains pronouns (he, she, his, her, it, that, this, they, their), carefully check the RECENT CONVERSATION to identify the reference
   - Maintain conversation continuity and remember what was discussed

3. **Response Style**:
   - Be direct, professional, and helpful
   - Do NOT start responses with greetings like "Hello" or "Hi" - jump straight to the answer
   - Use clear, concise language appropriate for workplace communication
   - Format lists and steps clearly when providing procedures

4. **Calculations**:
   - For mathematical calculations (salary, percentages, deductions), use: CALCULATOR: [expression]
   - Examples: 
     * CALCULATOR: 40000 * 0.3125 (basic salary)
     * CALCULATOR: 16 / 4 (quarterly leave)
   - Only use calculator for explicit calculation requests, not for policy explanations

5. **Specific Query Handling**:
   - **"Who is..." Questions**: 
     * Search thoroughly in employee database and management contacts
     * Provide: Full name + Position/Title + Email + Additional details (table, phone if available)
     * Example: "Who is the COO?" → "The COO (Chief Operating Officer) is Syed Sadhli Ahmed Roomy, who is also the Co-Founder of Acme AI Ltd."
     * For positions without specific names, explain the role clearly
   
   - **Employee Information**: 
     * Provide complete details: name, position, email, table number, blood group
     * For team/department queries, list all relevant members
     * Include reporting structure when relevant
   
   - **Policies**: 
     * Explain clearly with all relevant details, procedures, and requirements
     * Include specific numbers, percentages, and timeframes
     * Mention any exceptions or special cases
   
   - **Contact Info**: 
     * Always include email addresses and phone numbers from the knowledge base
     * For HR queries, mention: people@acmeai.tech or +8801313094329
     * For operations: project@acmeai.tech
   
   - **Dates & Deadlines**: 
     * Be specific with timelines and notice periods
     * Include any consequences of missing deadlines
   
   - **Procedures**: 
     * List steps clearly and in numbered order
     * Include who to contact at each step
     * Mention required documents or prerequisites

6. **Professional Standards**:
   - Maintain confidentiality and respect for all employees
   - Be neutral and fair in all responses
   - Encourage employees to verify critical information with HR when needed

PROVIDE YOUR ANSWER (NO GREETING, DIRECT RESPONSE):
"""

prompt = ChatPromptTemplate.from_template(optimized_prompt)

class HRChatbot:
    """Optimized HR Chatbot"""
    
    def __init__(self):
        self.context_mgr = ConversationContextManager()
        self.model = model
        self.retriever = retriever
    
    def answer(self, question: str, chat_history: Optional[List[Dict]] = None) -> str:
        """Generate contextually aware answer"""
        try:
            chat_history = chat_history or []
            question_stripped = question.strip()
            
            # DIRECT GREETING HANDLER - Bypass LLM entirely for greetings
            if self.context_mgr.is_greeting(question_stripped):
                if len(chat_history) == 0:
                    # First interaction - full greeting
                    return "Hello! I'm the HR Chatbot for Acme AI Ltd. How can I help you with HR-related questions today?"
                else:
                    # Subsequent greeting - shorter response
                    return "Hello! How can I assist you?"
            
            # Format history only if question has references
            if self.context_mgr.has_reference(question):
                history_text = self.context_mgr.format_history(chat_history)
            else:
                history_text = ""
            
            # Get relevant documents
            retrieved_docs = self.retriever.invoke(question)
            context_text = "\n---\n".join([doc.page_content for doc in retrieved_docs])
            
            # Build prompt
            full_prompt = prompt.format(
                history=history_text,
                context=context_text[:3000],  # Limit context size
                question=question
            )
            
            # Get response
            response = self.model.invoke(full_prompt)
            
            # Clean response - ALWAYS remove greetings
            cleaned = context_awareness_filter.invoke({"response": response})
            
            # Remove any greeting the LLM added
            cleaned = self._clean_followup(cleaned)
            
            # Handle calculations
            cleaned = self._handle_calc(cleaned, question)
            
            # Final validation
            if not cleaned or len(cleaned.strip()) < 5:
                return "I apologize, but I couldn't generate a proper response. Could you please rephrase your question?"
            
            return cleaned.strip()
            
        except Exception as e:
            print(f"Error in answer(): {str(e)}")
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
    """Main function"""
    return hr_chatbot.answer(question, chat_history)

def ask_hr_bot_api(question: str, chat_history: Optional[List[Dict]] = None, session_id: Optional[str] = None) -> str:
    """API wrapper"""
    return ask_hr_bot(question, chat_history, session_id)


if __name__ == "__main__":
    print("🤖 HR Chatbot with Context Awareness")
    print("Commands: 'clear' | 'quit'\n")
    
    chat_history = []
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
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
            print("\n\nGoodbye! 👋")
            break
