# ============================================================
# SEGMENT 5: GENERAL CALCULATOR & EXPORT
# Purpose: Basic arithmetic calculator and tool list export
# Tools: calculator
# ============================================================

class CalculatorInput(BaseModel):
    """Input for general calculations."""
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '25 * 0.3125' or '80 * 15')")

@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """
    Perform basic arithmetic calculations.
    
    Example usage:
        calculator("25000 * 0.3125")  # Calculate basic salary
        calculator("80 * 15")          # Calculate loss hour deduction
        calculator("(30000 + 5000) / 2")  # Average calculation
    
    Supports: +, -, *, /, parentheses
    """
    try:
        # Safe evaluation - only allow basic math operations
        allowed_chars = set('0123456789+-*/(). ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression. Only numbers and basic operators (+, -, *, /, parentheses) are allowed."
        
        result = eval(expression)
        return f"{expression} = {result:,.2f}" if isinstance(result, float) else f"{expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"

# ============================================================
# EXPORT ALL TOOLS
# This list is imported by main.py to access all tools
# ============================================================

hr_tools = [
    # Employee Lookup Tools
    find_employee,
    list_team_members,
    get_project_coordinator,
    
    # Salary Calculator Tools
    calculate_salary_breakdown,
    calculate_eid_bonus,
    calculate_late_deduction,
    calculate_loss_hour_deduction,
    
    # Leave & Benefits Tools
    calculate_annual_leave,
    calculate_leave_encashment,
    calculate_provident_fund,
    
    # General Calculator
    calculator,
]

print(f"✅ Loaded {len(hr_tools)} HR tools successfully!")