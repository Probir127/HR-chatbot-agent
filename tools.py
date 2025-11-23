"""
tools.py - HR Calculator Tool with Improved Context Filter
"""
from langchain_core.tools import tool
import re

@tool
def context_awareness_filter(response: str) -> str:
    """
    Filters out prompt templates and reasoning while preserving actual answers.
    Removes system instructions and context markers but keeps the real response.
    
    Args:
        response: The raw response from the model
        
    Returns:
        Cleaned response without prompt templates but with the actual answer
    """
    try:
        if not response or not response.strip():
            return "I apologize, but I couldn't generate a response."
            
        original_response = response.strip()
        
        # Step 1: Split by "RESPONSE:" if it exists
        if "RESPONSE:" in original_response:
            parts = original_response.split("RESPONSE:", 1)
            if len(parts) > 1 and parts[1].strip():
                original_response = parts[1].strip()
        
        # Step 2: Remove template header block
        cleaned_response = original_response
        
        patterns_to_remove_from_start = [
            r'^.*?You are an HR Chatbot for Acme AI Ltd\..*?(?=Hello|Hi|The |At |Yes|No|[A-Z][a-z])',
            r'^.*?CONTEXT FROM HR POLICIES:.*?(?=Hello|Hi|The |At |Yes|No|[A-Z][a-z])',
            r'^.*?HR KNOWLEDGE BASE:.*?(?=Hello|Hi|The |At |Yes|No|[A-Z][a-z])',
            r'^.*?INSTRUCTIONS:.*?(?=Hello|Hi|The |At |Yes|No|[A-Z][a-z])',
            r'^.*?CURRENT QUESTION:.*?(?=Hello|Hi|The |At |Yes|No|[A-Z][a-z])',
        ]
        
        for pattern in patterns_to_remove_from_start:
            before = cleaned_response
            cleaned_response = re.sub(pattern, '', cleaned_response, flags=re.DOTALL | re.IGNORECASE)
            if before != cleaned_response:
                break
        
        # Step 3: Remove specific instruction lines
        instruction_patterns = [
            r'You are an HR Chatbot for Acme AI Ltd\..*?(?:\n|$)',
            r'CONTEXT FROM HR POLICIES:.*?(?:\n|$)',
            r'HR KNOWLEDGE BASE:.*?(?:\n|$)',
            r'INSTRUCTIONS:.*?(?:\n|$)',
            r'CURRENT QUESTION:.*?(?:\n|$)',
            r'PROVIDE CONCISE ANSWER:.*?(?:\n|$)',
            r'###Question###.*?(?:\n|$)',
            r'###Answer###.*?(?:\n|$)',
        ]
        
        for pattern in instruction_patterns:
            cleaned_response = re.sub(pattern, '', cleaned_response, flags=re.IGNORECASE | re.MULTILINE)
        
        # Step 4: Clean up whitespace
        lines = [line.strip() for line in cleaned_response.split('\n') if line.strip()]
        cleaned_response = '\n'.join(lines)
        
        # Step 5: Final validation
        cleaned_response = cleaned_response.strip()
        
        if not cleaned_response or len(cleaned_response) < 3:
            return "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
        
        # Check if output still has template content
        bad_starts = [
            'You are an HR Chatbot',
            'CONTEXT FROM',
            'INSTRUCTIONS:',
            'HR KNOWLEDGE BASE:',
        ]
        
        for bad_start in bad_starts:
            if cleaned_response.startswith(bad_start):
                return "I apologize, but I encountered an issue generating a response. Please try again."
        
        return cleaned_response
        
    except Exception as e:
        print(f"Filter error: {e}")
        return "I apologize, but I encountered an error. Please try again."
    
@tool
def calculator(expression: str) -> str:
    """
    Basic arithmetic calculator for HR-related calculations.
    Use this for salary calculations, percentages, deductions, etc.
    
    Examples:
    - "40000 / 30 * 2" (Calculate 2 days unpaid leave from 40k salary)
    - "1800 * 5" (Calculate deduction for 5 late days)
    - "16 / 4" (Calculate quarterly leave allocation)
    - "50000 * 0.5" (Calculate Eid bonus)
    
    Args:
        expression: Mathematical expression (e.g., "50000 * 0.3125")
    
    Returns:
        String with calculation result
    """
    try:
        if not expression or expression.strip() == "":
            return "Please provide a mathematical expression to calculate."
        
        expression = expression.strip()
        
        # Safety check - only allow basic math operations
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "❌ Error: Only basic arithmetic operations (+, -, *, /, .) and numbers are allowed."
        
        # Prevent dangerous operations
        dangerous_patterns = ['import', 'exec', 'eval', '__', 'open', 'file']
        if any(pattern in expression.lower() for pattern in dangerous_patterns):
            return "❌ Error: Invalid expression for security reasons."
        
        # Evaluate safely
        result = eval(expression)
        
        # Format nicely
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 2)
        
        return f"🧮 Calculation: {expression} = {result:,}"
        
    except ZeroDivisionError:
        return "❌ Error: Cannot divide by zero."
    except SyntaxError:
        return "❌ Error: Invalid mathematical expression."
    except Exception as e:
        return f"❌ Calculation error: {str(e)}"

# List of all available tools
hr_tools = [calculator, context_awareness_filter]

# Dictionary mapping for easy access
TOOL_MAP = {tool.name: tool for tool in hr_tools}
