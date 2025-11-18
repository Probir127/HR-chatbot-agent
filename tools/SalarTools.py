# ============================================================
# SEGMENT 3: SALARY CALCULATOR TOOLS
# Purpose: Calculate salary breakdowns, bonuses, and deductions
# Tools: calculate_salary_breakdown, calculate_eid_bonus, 
#        calculate_late_deduction, calculate_loss_hour_deduction
# ============================================================

class SalaryCalculatorInput(BaseModel):
    """Input for salary breakdown calculations."""
    gross_salary: float = Field(description="Gross salary amount in Taka")

@tool(args_schema=SalaryCalculatorInput)
def calculate_salary_breakdown(gross_salary: float) -> str:
    """
    Calculate salary breakdown based on gross salary.
    
    Example usage:
        calculate_salary_breakdown(25000)
        calculate_salary_breakdown(30000)
    
    Formula:
        - Basic: 31.25% of gross
        - House Rent: 100% of basic
        - Medical: 60% of basic
        - Transport: 35% of basic
        - Mobile: 15% of basic
        - Internet: 10% of basic
    """
    basic = gross_salary * 0.3125
    house_rent = basic * 1.0
    medical = basic * 0.6
    transport = basic * 0.35
    mobile = basic * 0.15
    internet = basic * 0.10
    
    return f"""Salary Breakdown for Gross Salary: {gross_salary:,.2f} TK

• Basic Salary: {basic:,.2f} TK (31.25% of Gross)
• House Rent Allowance: {house_rent:,.2f} TK (100% of Basic)
• Medical Allowance: {medical:,.2f} TK (60% of Basic)
• Transport Allowance: {transport:,.2f} TK (35% of Basic)
• Mobile Allowance: {mobile:,.2f} TK (15% of Basic)
• Internet Allowance: {internet:,.2f} TK (10% of Basic)

Total: {basic + house_rent + medical + transport + mobile + internet:,.2f} TK"""

class EidBonusInput(BaseModel):
    """Input for Eid bonus calculation."""
    gross_salary: float = Field(description="Gross salary in Taka")
    months_served: int = Field(description="Number of months served at the company")

@tool(args_schema=EidBonusInput)
def calculate_eid_bonus(gross_salary: float, months_served: int) -> str:
    """
    Calculate Eid bonus based on service duration.
    
    Example usage:
        calculate_eid_bonus(25000, 8)  # 8 months served
        calculate_eid_bonus(30000, 4)  # 4 months served
    
    Rules:
        - 6+ months: 50% of gross salary
        - Less than 6 months: Prorated (25% * months / 6)
    """
    if months_served >= 6:
        bonus = gross_salary * 0.5
        return f"Eid Bonus: {bonus:,.2f} TK (50% of gross salary for confirmed employees with 6+ months service)"
    else:
        bonus = (gross_salary * 0.25 * months_served) / 6
        return f"Eid Bonus: {bonus:,.2f} TK (Prorated for {months_served} months of service)"

class LateDeductionInput(BaseModel):
    """Input for late deduction calculation."""
    late_days: int = Field(description="Number of days late in a month")
    daily_salary: float = Field(description="Daily salary amount in Taka")

@tool(args_schema=LateDeductionInput)
def calculate_late_deduction(late_days: int, daily_salary: float) -> str:
    """
    Calculate salary deduction for late arrivals.
    
    Example usage:
        calculate_late_deduction(5, 1000)  # 5 late days, 1000 TK daily
    
    Deduction Rules:
        3 days → 0.5 day salary
        5 days → 1 day salary
        8 days → 2 days salary
        10 days → 3 days salary
        13 days → 3.5 days salary
        15 days → 4 days salary
        18 days → 5 days salary
    """
    deduction_map = {
        3: 0.5, 5: 1, 8: 2, 10: 3, 13: 3.5, 15: 4, 18: 5
    }
    
    days_deducted = 0
    for threshold in sorted(deduction_map.keys()):
        if late_days >= threshold:
            days_deducted = deduction_map[threshold]
    
    if days_deducted == 0:
        return f"No deduction for {late_days} late days (less than 3 days)."
    
    deduction = daily_salary * days_deducted
    return f"""Late Deduction Calculation:
• Late Days: {late_days}
• Days Deducted: {days_deducted}
• Daily Salary: {daily_salary:,.2f} TK
• Total Deduction: {deduction:,.2f} TK"""

class LossHourInput(BaseModel):
    """Input for loss hour calculation."""
    loss_hours: float = Field(description="Number of loss hours")

@tool(args_schema=LossHourInput)
def calculate_loss_hour_deduction(loss_hours: float) -> str:
    """
    Calculate deduction for loss hours (unmet work hours).
    
    Example usage:
        calculate_loss_hour_deduction(15)  # 15 loss hours
    
    Rule: Each loss hour = 80 TK deduction
    """
    rate_per_hour = 80
    deduction = loss_hours * rate_per_hour
    
    return f"""Loss Hour Deduction:
• Loss Hours: {loss_hours}
• Rate per Hour: {rate_per_hour} TK
• Total Deduction: {deduction:,.2f} TK

Note: Each employee is expected to generate 8 hours of work daily. Any shortfall is considered a loss hour."""