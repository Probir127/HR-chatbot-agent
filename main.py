from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from vector import retriever 
from tools import hr_tools, find_employee, list_team_members, calculate_salary_breakdown, \
    calculate_eid_bonus, calculate_late_deduction, calculate_loss_hour_deduction, \
    calculate_annual_leave, calculate_leave_encashment, calculate_provident_fund, \
    calculator, get_project_coordinator
import re

# --- 1. Setup ---
model = OllamaLLM(
    model="llama3.2",
    temperature=0.1,
    max_tokens=1000,
)

# Enhanced template with tool usage instructions
template = """
You are an HR Chatbot for Acme AI Ltd. Answer questions based on the provided HR policy context and available tools.

AVAILABLE TOOLS:
- you are good at small talk too
- find_employee(name, email, position, table): Find employee details
- list_team_members(table): List all team members for a table
- get_project_coordinator(table): Get project coordinator for a table
- calculate_salary_breakdown(gross_salary): Break down salary components
- calculate_eid_bonus(gross_salary, months_served): Calculate Eid bonus
- calculate_late_deduction(late_days, daily_salary): Calculate late deductions
- calculate_loss_hour_deduction(loss_hours): Calculate loss hour deductions
- calculate_annual_leave(months_served, quarters_completed): Calculate annual leave
- calculate_leave_encashment(unused_leave_days, daily_wage): Calculate leave encashment
- calculate_provident_fund(years_of_service, basic_salary): Calculate provident fund
- calculator(expression): Basic arithmetic
- 
CONTEXT:
{context}

QUESTION: {question}

Instructions:
1. ONLY answer if there is a clear, specific question
2. If the question needs a calculation or employee lookup, respond with: USE_TOOL: tool_name(parameters)
3. If the context has the answer, provide it directly and concisely
4. Do NOT introduce yourself or role-play as an employee
5. Be professional and factual

Answer: 
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model 

# Tool mapping for easy execution
tool_map = {
    'find_employee': find_employee,
    'list_team_members': list_team_members,
    'get_project_coordinator': get_project_coordinator,
    'calculate_salary_breakdown': calculate_salary_breakdown,
    'calculate_eid_bonus': calculate_eid_bonus,
    'calculate_late_deduction': calculate_late_deduction,
    'calculate_loss_hour_deduction': calculate_loss_hour_deduction,
    'calculate_annual_leave': calculate_annual_leave,
    'calculate_leave_encashment': calculate_leave_encashment,
    'calculate_provident_fund': calculate_provident_fund,
    'calculator': calculator,
}

def parse_tool_call(response):
    """Extract tool name and parameters from response."""
    pattern = r'USE_TOOL:\s*(\w+)\((.*?)\)'
    match = re.search(pattern, response)
    if match:
        tool_name = match.group(1)
        params_str = match.group(2)
        return tool_name, params_str
    return None, None

def execute_tool(tool_name, params_str):
    """Execute the specified tool with parameters."""
    if tool_name not in tool_map:
        return f"Error: Tool '{tool_name}' not found."
    
    tool = tool_map[tool_name]
    
    try:
        # Parse parameters
        params = []
        if params_str.strip():
            # Handle quoted strings and numbers
            param_parts = []
            current = ""
            in_quotes = False
            
            for char in params_str:
                if char == '"' or char == "'":
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    param_parts.append(current.strip())
                    current = ""
                    continue
                current += char
            
            if current.strip():
                param_parts.append(current.strip())
            
            # Convert parameters to appropriate types
            for param in param_parts:
                param = param.strip().strip('"').strip("'")
                # Try to convert to number
                try:
                    if '.' in param:
                        params.append(float(param))
                    else:
                        params.append(int(param))
                except ValueError:
                    params.append(param)
        
        # Execute tool
        result = tool.invoke({"name": params[0]} if len(params) == 1 and tool_name == "find_employee" 
                           else {k: v for k, v in zip(tool.args_schema.__fields__.keys(), params)})
        return result
    
    except Exception as e:
        return f"Error executing tool: {str(e)}"

def process_query(question, max_iterations=3):
    """Process a query with potential tool calls."""
    iteration = 0
    context_text = ""
    
    while iteration < max_iterations:
        # Retrieve context from vector store
        retrieved_docs = retriever.invoke(question)
        context_text = "\n---\n".join([doc.page_content for doc in retrieved_docs])
        
        # Get LLM response
        result = chain.invoke({
            "question": question, 
            "context": context_text 
        })
        
        # Check if tool usage is needed
        tool_name, params_str = parse_tool_call(result)
        
        if tool_name:
            print(f"\n Using tool: {tool_name}({params_str})")
            tool_result = execute_tool(tool_name, params_str)
            print(f" Tool result:\n{tool_result}\n")
            
            # Add tool result to context for next iteration
            context_text += f"\n\nTOOL RESULT:\n{tool_result}"
            
            # Ask LLM to formulate final answer with tool result
            final_prompt = f"""Based on the following tool result, provide a clear and helpful answer to the user's question.

QUESTION: {question}

TOOL RESULT:
{tool_result}

Provide a conversational answer incorporating this information:"""
            
            final_result = model.invoke(final_prompt)
            return final_result
        else:
            # No tool needed, return direct answer
            return result
        
        iteration += 1
    
    return "I apologize, but I couldn't process your request after multiple attempts."

# --- Main Loop ---
print("=" * 60)
print(" HR Chatbot for Acme AI Ltd.")
print("=" * 60)
print("\nAvailable commands:")
print("  - Ask any HR-related question")
print("  - Type 'tools' to see available tools")
print("  - Type 'q' to quit")
print("=" * 60)

while True: 
    print("\n" + "-" * 60)
    question = input("\n Your question: ").strip()
    
    if question.lower() == 'q':
        print("\n Thank you for using HR Chatbot. Goodbye!\n")
        break
    
    if question.lower() == 'tools':
        print("\n Available Tools:")
        print("-" * 60)
        for tool in hr_tools:
            print(f"\nâ–ª {tool.name}")
            print(f"  {tool.description}")
        continue
    
    if not question:
        print("  Please enter a question.")
        continue
    
    print("\n Processing your question...\n")
    
    try:
        result = process_query(question)
        print("=" * 60)
        print(" Answer:")
        print("=" * 60)
        print(result)
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")