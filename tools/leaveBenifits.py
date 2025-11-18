# ============================================================
# SEGMENT 4: LEAVE & BENEFITS CALCULATOR TOOLS
# Purpose: Calculate leave entitlements and provident fund
# Tools: calculate_annual_leave, calculate_leave_encashment, 
#        calculate_provident_fund
# ============================================================

class LeaveBalanceInput(BaseModel):
    """Input for leave balance calculation."""
    months_served: int = Field(description="Number of months served at the company")
    quarters_completed: int = Field(description="Number of quarters completed (1-4)")

@tool(args_schema=LeaveBalanceInput)
def calculate_annual_leave(months_served: int, quarters_completed: int) -> str:
    """
    Calculate annual leave entitlement.
    
    Example usage:
        calculate_annual_leave(15, 3)  # 15 months, 3 quarters done
    
    Rules:
        - 16 days total after 1 year
        - 4 days per quarter
        - Minimum 12 months service required
    """
    if months_served < 12:
        return "Annual leave is only available after completing one year of service."
    
    total_annual_leave = 16
    leave_per_quarter = 4
    available_leave = quarters_completed * leave_per_quarter
    
    return f"""Annual Leave Entitlement:
• Total Annual Leave: {total_annual_leave} days (after 1 year)
• Leave per Quarter: {leave_per_quarter} days
• Quarters Completed: {quarters_completed}
• Available Leave: {available_leave} days

Note: Up to 4 days of unused leave per quarter can be encashed."""

class EncashmentInput(BaseModel):
    """Input for leave encashment calculation."""
    unused_leave_days: int = Field(description="Number of unused leave days in a quarter")
    daily_wage: float = Field(description="Daily wage in Taka")

@tool(args_schema=EncashmentInput)
def calculate_leave_encashment(unused_leave_days: int, daily_wage: float) -> str:
    """
    Calculate leave encashment amount.
    
    Example usage:
        calculate_leave_encashment(3, 800)  # 3 unused days, 800 TK daily wage
    
    Rules:
        - Maximum 4 days per quarter can be encashed
        - Paid at daily wage rate
    """
    max_encashable = 4
    
    if unused_leave_days > max_encashable:
        encashable_days = max_encashable
        message = f"(Maximum {max_encashable} days per quarter can be encashed)"
    else:
        encashable_days = unused_leave_days
        message = ""
    
    encashment_amount = encashable_days * daily_wage
    
    return f"""Leave Encashment Calculation:
• Unused Leave Days: {unused_leave_days}
• Encashable Days: {encashable_days} {message}
• Daily Wage: {daily_wage:,.2f} TK
• Encashment Amount: {encashment_amount:,.2f} TK"""

class ProvidentFundInput(BaseModel):
    """Input for provident fund calculation."""
    years_of_service: int = Field(description="Total years of service")
    basic_salary: float = Field(description="Monthly basic salary in Taka")

@tool(args_schema=ProvidentFundInput)
def calculate_provident_fund(years_of_service: int, basic_salary: float) -> str:
    """
    Calculate provident fund entitlement.
    
    Example usage:
        calculate_provident_fund(5, 10000)   # 5 years, 10000 TK basic
        calculate_provident_fund(12, 15000)  # 12 years, 15000 TK basic
    
    Rules:
        - Less than 3 years: Not eligible
        - 3-10 years: 1 month basic per year
        - Over 10 years: 1.5 months basic per year
    """
    if years_of_service < 3:
        return "Provident fund is only available after completing 3 years of continuous service."
    elif years_of_service <= 10:
        months_entitled = years_of_service * 1
        total_amount = basic_salary * months_entitled
        return f"""Provident Fund Calculation:
• Years of Service: {years_of_service}
• Basic Salary: {basic_salary:,.2f} TK
• Entitlement: {months_entitled} months of basic salary
• Total Amount: {total_amount:,.2f} TK

(1 month's basic salary per year for 3-10 years of service)"""
    else:
        months_entitled = years_of_service * 1.5
        total_amount = basic_salary * months_entitled
        return f"""Provident Fund Calculation:
• Years of Service: {years_of_service}
• Basic Salary: {basic_salary:,.2f} TK
• Entitlement: {months_entitled} months of basic salary
• Total Amount: {total_amount:,.2f} TK

(1.5 months' basic salary per year for over 10 years of service)"""