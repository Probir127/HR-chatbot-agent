# ============================================================
# SEGMENT 2: EMPLOYEE LOOKUP TOOLS
# Purpose: Find employees, list teams, get coordinators
# Tools: find_employee, list_team_members, get_project_coordinator
# ============================================================

class EmployeeLookupInput(BaseModel):
    """Input schema for employee lookup."""
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
    
    Example usage:
        find_employee(name="Punom")
        find_employee(email="punom.acmeai@gmail.com")
        find_employee(position="Team Lead")
        find_employee(table="1-A")
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
    List all team members for a specific table.
    
    Example usage:
        list_team_members("1-A")
        list_team_members("2-B")
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
    Get the project coordinator for a specific table.
    
    Example usage:
        get_project_coordinator("1-A")
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