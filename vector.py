# vector.py - Updated version with MarkdownHeaderTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
import os 
import json

# --- 1. Configuration ---

PDF_PATH = 'General HR Queries.pdf'
EMPLOYEE_DATA_PATH = 'employees.json'

embeddings = OllamaEmbeddings(
    model="mxbai-embed-large",
)

db_location = "./chroma_hr_db"

# Check if the database needs to be built
add_documents = not os.path.exists(db_location)

# --- 2. Ingestion or Loading Logic ---

if add_documents:
    print("Building new vector store from PDF and employee data...")
    
    all_documents = []
    
    # **STEP A: Load the PDF document**
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load() 
    
    # **STEP B: Use MarkdownHeaderTextSplitter for better structure**
    # Define headers to split on (since PDF uses #, ##, ### for headings)
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"), 
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]
    
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False
    )
    
    # Process each page with markdown splitter
    for page in pages:
        try:
            # Split the page content using markdown headers
            split_docs = markdown_splitter.split_text(page.page_content)
            all_documents.extend(split_docs)
        except Exception as e:
            print(f"Warning: Could not split page with markdown: {e}")
            # Fallback: add the page as-is
            all_documents.append(page)
    
    print(f"Processed PDF into {len(all_documents)} markdown-structured documents.")

    # **STEP C: Load and process employee data**
    try:
        with open(EMPLOYEE_DATA_PATH, 'r', encoding='utf-8') as f:
            employee_data = json.load(f)
        
        # Convert employee data to documents
        employee_docs = []
        
        # Process Operation Team
        for employee in employee_data["EmployeeDetails"]["OperationTeam"]:
            doc_text = f"""
            Employee: {employee["EmployeeName"]}
            Position: {employee["Position"]}
            Email: {employee["Email"]}
            Table: {employee["Table"]}
            Blood Group: {employee["BloodGroup"]}
            Team: Operation Team
            """
            employee_docs.append(Document(
                page_content=doc_text,
                metadata={"source": "employees.json", "type": "employee", "team": "operation"}
            ))
        
        # Process Strategic Interventions
        for employee in employee_data["EmployeeDetails"]["StrategicInterventions"]:
            doc_text = f"""
            Employee: {employee["EmployeeName"]}
            Position: {employee["Position"]}
            Email: {employee["Email"]}
            Table: {employee["Table"]}
            Blood Group: {employee["BloodGroup"]}
            Team: Strategic Interventions
            """
            employee_docs.append(Document(
                page_content=doc_text,
                metadata={"source": "employees.json", "type": "employee", "team": "strategic"}
            ))
        
        # Process Additional Teams
        for employee in employee_data["EmployeeDetails"]["AdditionalTeams"]:
            doc_text = f"""
            Employee: {employee["EmployeeName"]}
            Position: {employee["Position"]}
            Email: {employee["Email"]}
            Table: {employee["Table"]}
            Blood Group: {employee["BloodGroup"]}
            Team: Additional Teams
            """
            employee_docs.append(Document(
                page_content=doc_text,
                metadata={"source": "employees.json", "type": "employee", "team": "additional"}
            ))
        
        # Process Project Coordinators
        for coordinator in employee_data["EmployeeDetails"]["ProjectCoordinators"]:
            doc_text = f"""
            Project Coordinator: {coordinator["Name"]}
            Tables: {', '.join(coordinator["Tables"])}
            Email: {coordinator["Email"]}
            Type: Project Coordinator
            """
            employee_docs.append(Document(
                page_content=doc_text,
                metadata={"source": "employees.json", "type": "project_coordinator"}
            ))
        
        # Process Management Contacts
        for contact in employee_data["EmployeeDetails"]["ManagementTeamContacts"]:
            position = contact.get("Position", "Management")
            doc_text = f"""
            Management: {contact["Name"]}
            Position: {position}
            Email: {contact["Email"]}
            Type: Management Contact
            """
            employee_docs.append(Document(
                page_content=doc_text,
                metadata={"source": "employees.json", "type": "management"}
            ))
        
        all_documents.extend(employee_docs)
        print(f"Added {len(employee_docs)} employee records to the database.")
        
    except Exception as e:
        print(f"Warning: Could not load employee data: {e}")

    # **STEP D: Final splitting for any large chunks**
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    documents = text_splitter.split_documents(all_documents)
    print(f"Total documents after final splitting: {len(documents)}")

    # **STEP E: Create, embed, and persist the database**
    vector_store = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings, 
        persist_directory=db_location,
    )
    print(f"Successfully built and saved Chroma DB at: {db_location}")
    
else:
    # Load the existing database if it already exists
    print(f"Loading existing vector store from: {db_location}")
    vector_store = Chroma(
        persist_directory=db_location, 
        embedding_function=embeddings
    )

# --- 3. Create Retriever ---
retriever = vector_store.as_retriever(search_kwargs={"k": 10})

print("Retriever initialized successfully.")
