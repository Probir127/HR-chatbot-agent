# ============================================================
# SEGMENT 1: IMPORTS AND DATA LOADING
# Purpose: Load employee and policy data from JSON files
# ============================================================

from langchain.tools import tool
from pydantic import BaseModel, Field
from typing import Optional
import json

def load_employee_data():
    """
    Load employee data from JSON files.
    
    Returns:
        tuple: (employees_dict, policies_dict) or (None, None) if files not found
    """
    try:
        with open('employees.json', 'r') as f:
            employees = json.load(f)
        with open('employee_data.json', 'r') as f:
            policies = json.load(f)
        return employees, policies
    except FileNotFoundError:
        return None, None

# This function is used by all other tools to access data