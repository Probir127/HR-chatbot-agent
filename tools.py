"""
tools.py - HR Calculator Tool
"""
from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """
    Basic arithmetic calculator for HR-related calculations.
    Use this for salary calculations, percentages, deductions, etc.
    
    Examples:
    - "50000 * 0.3125" (Calculate basic salary from gross)
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
            return "Please provide a mathematical expression to calculate. Example: '50000 * 0.3125'"
        
        # Clean the expression
        expression = expression.strip()
        
        # Safety check - only allow basic math operations and numbers
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "❌ Error: Only basic arithmetic operations (+, -, *, /, .) and numbers are allowed."
        
        # Additional safety - prevent dangerous operations
        dangerous_patterns = ['import', 'exec', 'eval', '__', 'open', 'file']
        if any(pattern in expression.lower() for pattern in dangerous_patterns):
            return "❌ Error: Invalid expression for security reasons."
        
        # Evaluate the expression safely
        result = eval(expression)
        
        # Format the result nicely
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 2)
        
        return f"🧮 Calculation: {expression} = {result:,}"
        
    except ZeroDivisionError:
        return "❌ Error: Cannot divide by zero."
    except SyntaxError:
        return "❌ Error: Invalid mathematical expression. Please check your input."
    except Exception as e:
        return f"❌ Calculation error: {str(e)}"

# List of all available tools (only calculator for now)
hr_tools = [calculator]

# Dictionary mapping for easy access
TOOL_MAP = {tool.name: tool for tool in hr_tools}

if __name__ == "__main__":
    # Test the calculator
    print("🧪 Testing HR Calculator...\n")
    
    test_cases = [
        "50000 * 0.3125",
        "1800 * 5", 
        "16 / 4",
        "50000 * 0.5",
        "80 * 10",
        "15000 + 2500 + 1800"
    ]
    
    for test in test_cases:
        print(f"Input: {test}")
        result = calculator.invoke({"expression": test})
        print(f"Result: {result}\n")