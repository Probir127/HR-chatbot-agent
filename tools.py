from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
import json

# Load employee data
def load_employee_data():
    """Load employee data from JSON files."""
    try:
        with open('employees.json', 'r') as f:
            employees = json.load(f)
        with open('employee_data.json', 'r') as f:
            policies = json.load(f)
        return employees, policies
    except FileNotFoundError:
        return None, None

# ====================
# EMPLOYEE LOOKUP TOOLS
# ====================

class EmployeeLookupInput(BaseModel):
    """Input for employee lookup."""
    name: Optional[str] = Field(None, description="Employee name to search for")
    email: Optional[str] = Field(None, description="Employee email to search for")
    position: Optional[str] = Field(None, description="Position/role to search for")
    table: Optional[str] = Field(None, description="Table number to search for")

@tool(args_schema=EmployeeLookupInput)
def find_employee(
    name: Optional[str] = None,
    email: Optional[str] = None,
    position: Optional[str] = None,
    table: Optional[str] = None
) -> str:
    """
    Find employee details by name, email, position, or table number.
    Returns employee information including name, email, table, blood group, and position.
    """
    employees, _ = load_employee_data()
    if not employees:
        return "Error: Could not load employee data."
    
    results = []
    
    # Search in Operation Team
    for emp in employees["EmployeeDetails"]["OperationTeam"]:
        match = True
        if name and name.lower() not in emp["EmployeeName"].lower():
            match = False
        if email and email.lower() not in emp["Email"].lower():
            match = False
        if position and position.lower() not in emp["Position"].lower():
            match = False
        if table and table.upper() != emp["Table"].upper():
            match = False
        
        if match:
            results.append(
                f"Name: {emp['EmployeeName']}\n"
                f"Email: {emp['Email']}\n"
                f"Position: {emp['Position']}\n"
                f"Table: {emp['Table']}\n"
                f"Blood Group: {emp['BloodGroup']}"
            )
    
    # Search in Management Team
    if position:
        for mgr in employees["EmployeeDetails"]["ManagementTeamContacts"]:
            if position.lower() in mgr["Position"].lower():
                results.append(
                    f"Name: {mgr['Name']}\n"
                    f"Position: {mgr['Position']}"
                )
    
    if results:
        return "\n\n---\n\n".join(results)
    else:
        return "No employees found matching the search criteria."

@tool
def list_team_members(table: str) -> str:
    """
    List all team members for a specific table (e.g., '1-A', '2-B', '3-C').
    Shows team lead, assistant team lead, and production officers.
    """
    employees, _ = load_employee_data()
    if not employees:
        return "Error: Could not load employee data."
    
    table = table.upper()
    team_members = []
    
    for emp in employees["EmployeeDetails"]["OperationTeam"]:
        if emp["Table"].upper() == table:
            team_members.append(emp)
    
    if not team_members:
        return f"No team members found for table {table}."
    
    # Sort by position hierarchy
    position_order = {"Team Lead": 1, "Assistant Team Lead": 2, "Production Officer": 3}
    team_members.sort(key=lambda x: position_order.get(x["Position"], 99))
    
    result = f"Team Members for Table {table}:\n\n"
    for emp in team_members:
        result += f"• {emp['EmployeeName']} - {emp['Position']}\n  Email: {emp['Email']}\n"
    
    return result

@tool
def get_project_coordinator(table: str) -> str:
    """
    Get the project coordinator for a specific table (1-A, 1-B, 1-C, 2-A, etc.).
    """
    table = table.upper()
    
    coordinators = {
        "1-A": "Md Rashed Khan Milon",
        "1-B": "Md Rashed Khan Milon",
        "1-C": "Md Rashed Khan Milon",
        "2-A": "Tariqul Islam Bablu",
        "2-B": "Tariqul Islam Bablu",
        "2-C": "Tariqul Islam Bablu",
        "3-A": "Md Ramjan Islam",
        "3-B": "Md Ramjan Islam",
        "3-C": "Md Ramjan Islam",
    }
    
    coordinator = coordinators.get(table)
    if coordinator:
        return f"The project coordinator for Table {table} is {coordinator}."
    else:
        return f"No project coordinator found for table {table}."

# ====================
# SALARY CALCULATOR TOOLS
# ====================

class SalaryCalculatorInput(BaseModel):
    """Input for salary calculations."""
    gross_salary: float = Field(description="Gross salary amount in Taka")

@tool(args_schema=SalaryCalculatorInput)
def calculate_salary_breakdown(gross_salary: float) -> str:
    """
    Calculate salary breakdown based on gross salary.
    Returns basic salary and all allowances (house rent, medical, transport, mobile, internet).
    """
    _, policies = load_employee_data()
    if not policies:
        return "Error: Could not load policy data."
    
    # Basic salary is 31.25% of gross
    basic = gross_salary * 0.3125
    
    # All other allowances are percentages of basic salary
    house_rent = basic * 1.0  # 100% of basic
    medical = basic * 0.6      # 60% of basic
    transport = basic * 0.35   # 35% of basic
    mobile = basic * 0.15      # 15% of basic
    internet = basic * 0.10    # 10% of basic
    
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
    Calculate Eid bonus based on gross salary and months of service.
    Employees with 6+ months get 50% of gross. Less than 6 months get prorated bonus.
    """
    if months_served >= 6:
        bonus = gross_salary * 0.5
        return f"Eid Bonus: {bonus:,.2f} TK (50% of gross salary for confirmed employees with 6+ months service)"
    else:
        # Prorated: 25% of gross * months / probation period (6 months)
        bonus = (gross_salary * 0.25 * months_served) / 6
        return f"Eid Bonus: {bonus:,.2f} TK (Prorated for {months_served} months of service)"

class LateDeductionInput(BaseModel):
    """Input for late deduction calculation."""
    late_days: int = Field(description="Number of days late in a month")
    daily_salary: float = Field(description="Daily salary amount in Taka")

@tool(args_schema=LateDeductionInput)
def calculate_late_deduction(late_days: int, daily_salary: float) -> str:
    """
    Calculate salary deduction based on number of late days.
    Returns the deduction amount based on company policy.
    """
    deduction_map = {
        3: 0.5,   # Half day
        5: 1,     # 1 day
        8: 2,     # 2 days
        10: 3,    # 3 days
        13: 3.5,  # 3.5 days
        15: 4,    # 4 days
        18: 5,    # 5 days
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
    Calculate salary deduction based on loss hours.
    Each loss hour costs 80 TK according to company policy.
    """
    rate_per_hour = 80
    deduction = loss_hours * rate_per_hour
    
    return f"""Loss Hour Deduction:
• Loss Hours: {loss_hours}
• Rate per Hour: {rate_per_hour} TK
• Total Deduction: {deduction:,.2f} TK

Note: Each employee is expected to generate 8 hours of work daily. Any shortfall is considered a loss hour."""

# ====================
# LEAVE CALCULATOR TOOLS
# ====================

class LeaveBalanceInput(BaseModel):
    """Input for leave balance calculation."""
    months_served: int = Field(description="Number of months served at the company")
    quarters_completed: int = Field(description="Number of quarters completed (1-4)")

@tool(args_schema=LeaveBalanceInput)
def calculate_annual_leave(months_served: int, quarters_completed: int) -> str:
    """
    Calculate available annual/earned leave days.
    Employees get 16 days after one year, distributed across 4 quarters (4 days per quarter).
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
    Up to 4 days per quarter can be encashed at daily wage rate.
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
    Calculate provident fund entitlement based on years of service.
    3-10 years: 1 month basic per year. Over 10 years: 1.5 months basic per year.
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

# ====================
# GENERAL CALCULATOR
# ====================

class CalculatorInput(BaseModel):
    """Input for general calculations."""
    expression: str = Field(description="Mathematical expression to evaluate (e.g., '25 * 0.3125' or '80 * 15')")

@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """
    Perform basic arithmetic calculations.
    Useful for calculating percentages, multiplications, divisions, etc.
    Example: '25000 * 0.3125' for calculating basic salary.
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

# ====================
# EXPORT ALL TOOLS
# ====================

# List of all available tools for the agent
hr_tools = [
    find_employee,
    list_team_members,
    get_project_coordinator,
    calculate_salary_breakdown,
    calculate_eid_bonus,
    calculate_late_deduction,
    calculate_loss_hour_deduction,
    calculate_annual_leave,
    calculate_leave_encashment,
    calculate_provident_fund,
    calculator,
]