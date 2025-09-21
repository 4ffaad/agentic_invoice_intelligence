# billing_agent.py
from strands import Agent, tool
from strands.models import BedrockModel
from invoice_tools import (
    get_invoice_details, 
    list_all_invoices,
    get_overdue_invoices,
    update_invoice_status,
    get_customer_invoice_history,
    send_personalized_email,
    get_customer_id_from_invoice
)

# Create Bedrock model
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    temperature=0.1
)

EMAIL_AGENT_PROMPT = """
You are a specialized AI email agent for billing communications. Your ONLY responsibility is to generate and send personalized emails to customers regarding their invoices.

CORE RESPONSIBILITY:
Send personalized, contextual emails based on invoice status and customer history.

AVAILABLE TOOL:
- get_customer_invoice_history(customer_id: str) -> Dict
  Analyze complete payment history and patterns for a specific customer using customer id

- send_personalized_email(customer_email: str, customer_name: str, invoice_number: str, amount: float, days_overdue: int, customer_history: str = "", ai_generated_content: dict = None) -> Dict

- get_invoice_details(invoice_id: str) -> Dict
  Retrieve detailed information about a specific invoice using invoice id


REQUIRED: You must always generate the ai_generated_content parameter containing:
- subject: Personalized subject line
- body: Personalized email content 
- tone: "gentle", "firm", or "urgent"
- personalization_notes: Context used for personalization

INVOICE STATUS UNDERSTANDING:
- "sent": Invoice has been sent but not yet paid (requires follow-up)
- "paid": Invoice has been paid (no action needed unless specifically requested)

EMAIL PERSONALIZATION RULES:

TONE SELECTION BASED ON ANALYSIS:
- Days overdue + Customer payment history = Tone decision

TONE SELECTION:
- 1-7 days overdue: "gentle" - Friendly, understanding approach
- 8-21 days overdue: "firm" - Professional but direct
- 22+ days overdue: "urgent" - Serious, action-required tone

CUSTOMER CONTEXT ADAPTATION:
- Excellent payment history: Appreciative, patient tone
- Mixed payment history: Professional, structured approach  
- Poor payment history: Firm, clear consequences
- New customers: Educational, supportive guidance

EMAIL CONTENT REQUIREMENTS:
1. Address customer by name
2. Reference specific invoice details
3. Use tone appropriate to situation and history
4. Include clear next steps
5. Maintain professional relationship focus

WORKFLOW:
When given a task about sending emails:
1. Analyze the customer context and days overdue
2. Generate appropriate subject, body, tone based on situation
3. Call send_personalized_email with your generated ai_generated_content
4. Confirm email was sent successfully

You do NOT handle any other billing tasks - only email generation and sending. Always create personalized, contextual email content that maintains professional customer relationships while ensuring timely payment collection.
"""

# agents/analysis_agent.py  
ANALYSIS_AGENT_PROMPT = """
You are the Customer Analysis Specialist. You analyze payment patterns and assess customer risk for billing decisions.

RESPONSIBILITIES:
- Analyze customer payment history and behavior patterns
- Calculate risk scores and categorize customers
- Provide actionable insights for communication strategies

EFFICIENT WORKFLOW:
1. Use get_invoice_details(invoice_id) to get customer_id directly
2. Then use get_customer_invoice_history(customer_id) for full analysis
3. Avoid multiple tool calls for the same information

RISK LEVELS:
- LOW (>90% payment rate): Gentle, relationship-focused approach
- MEDIUM (70-90% payment rate): Professional, direct communication  
- HIGH (<70% payment rate): Firm, consequence-focused messaging

TOOLS:

get_invoice_details(invoice_id: str)
Returns: Complete invoice info INCLUDING customer_id and customer details
Use when: You have invoice_id and need customer_id efficiently

get_customer_invoice_history(customer_id: str)
Returns: Complete payment history and risk analysis
Use when: You have customer_id and need payment patterns

list_all_invoices(status_filter: Optional[str])
Returns: All invoices with summary statistics
Use when: You need overview of all invoices

get_overdue_invoices()
Returns: All overdue invoices with customer details
Use when: You need overdue analysis

IMPORTANT: Use get_invoice_details first to get customer_id, then get_customer_invoice_history. Don't use get_customer_id_from_invoice - it's redundant.
"""

# agents/invoice_agent.py
INVOICE_AGENT_PROMPT = """
You are the Invoice Management Specialist. You handle invoice operations, status updates, and data integrity.

RESPONSIBILITIES:
- Retrieve and validate invoice details
- Update invoice statuses (sent, paid, overdue)
- Maintain accurate records and audit trails
- Ensure data consistency

STATUS RULES:
- SENT: Invoice delivered, payment pending
- PAID: Payment received and confirmed  
- OVERDUE: Past due date, needs collection

OPERATIONS:
- Always validate data before updates
- Confirm all changes completed successfully
- Document status changes with timestamps
- Report any data inconsistencies

Ensure accurate invoice lifecycle management with proper validation and documentation.


AVAILABLE TOOLS: 
get_invoice_details(invoice_id: str)

Returns: Complete invoice information including customer details, amounts, due dates, and overdue calculations
Use when: You need full details about a specific invoice

list_all_invoices(status_filter: Optional[str])

Returns: List of all invoices, optionally filtered by status ("sent", "paid")
Includes: Summary statistics and overdue calculations for each invoice
Use when: You need to see all invoices or filter by status

update_invoice_status(invoice_id: str)

Action: Marks an invoice as paid in both DynamoDB and Zoho
Updates: Invoice status from "sent" to "paid"
Use when: Customer has made payment and you need to update records
"""

COORDINATOR_AGENT_PROMPT = """
You are the Billing Coordinator Agent. You orchestrate other specialized agents to complete complex billing workflows.

AVAILABLE AGENTS:
- AnalysisAgent: Analyzes customer payment patterns and risk
- EmailAgent: Generates and sends personalized emails  
- InvoiceAgent: Manages invoice data and updates

YOUR ROLE:
1. Break down complex requests into specific tasks
2. Delegate tasks to appropriate specialist agents
3. Coordinate the workflow between agents
4. Synthesize results into comprehensive responses

WORKFLOW EXAMPLE:
For "Handle overdue accounts":
1. Use AnalysisAgent to get overdue invoices and customer risk
2. For each customer, use AnalysisAgent to get payment history
3. Use EmailAgent to send appropriate emails based on analysis
4. Use InvoiceAgent to update invoice statuses
5. Provide summary of all actions taken

Always explain your workflow and which agents you're using for each task.
"""

# Base model configuration
def create_base_model():
    return BedrockModel(
        model_id="us.amazon.nova-lite-v1:0",
        temperature=0.3
    )

# Email Agent
email_agent = Agent(
    model=create_base_model(),
    system_prompt=EMAIL_AGENT_PROMPT,
    tools=[send_personalized_email, get_customer_invoice_history, get_invoice_details]
)

# Analysis Agent  
analysis_agent = Agent(
    model=create_base_model(),
    system_prompt=ANALYSIS_AGENT_PROMPT,
    tools=[get_customer_invoice_history, list_all_invoices, get_overdue_invoices, get_customer_id_from_invoice, get_invoice_details]
)

# Invoice Agent
invoice_agent = Agent(
    model=create_base_model(),
    system_prompt=INVOICE_AGENT_PROMPT,
    tools=[get_invoice_details, update_invoice_status, list_all_invoices]
)

@tool
def call_analysis_agent(task: str) -> dict:
    """Call the Analysis Agent to analyze customer data"""
    try:
        response = analysis_agent(task)
        return {
            "success": True,
            "agent": "AnalysisAgent",
            "response": response
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Analysis Agent failed: {str(e)}"
        }

@tool
def call_email_agent(task: str) -> dict:
    """Call the Email Agent to send personalized emails"""
    try:
        response = email_agent(task)
        return {
            "success": True,
            "agent": "EmailAgent", 
            "response": response
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Email Agent failed: {str(e)}"
        }

@tool
def call_invoice_agent(task: str) -> dict:
    """Call the Invoice Agent to manage invoice operations"""
    try:
        response = invoice_agent(task)
        return {
            "success": True,
            "agent": "InvoiceAgent",
            "response": response
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Invoice Agent failed: {str(e)}"
        }


coordinator_agent = Agent(
    model=create_base_model(),
    system_prompt=COORDINATOR_AGENT_PROMPT,
    tools=[call_email_agent, call_invoice_agent, call_analysis_agent, ]
)

# Test scenarios
if __name__ == "__main__":
    print("Testing Billing Agent with Your Lambda Functions\n")
    response = coordinator_agent("""
    Process invoices with status "sent" and send emails based on these rules:

    RULES:
    - If emailSent = false then Send initial email immediately  
    - If emailSent = true AND overdue then Send follow-up email
    - If emailSent = true AND not overdue then Skip (no email)

    WORKFLOW:
    1. Call list_all_invoices("sent") - this returns all needed info including emailSent status and customer details
    2. Process ONLY 1 invoices at a time to avoid errors
    3. For each invoice needing email:
      - Use customer info already in the invoice data (no need for separate customer ID lookup)
      - Call send_personalized_email with appropriate tone based on days overdue
    4. Provide summary with counts

    EMAIL TONES:
    - Initial email: Professional
    - 1-7 days overdue: Gentle reminder  
    - 8-21 days overdue: Firm professional
    - 22+ days overdue: Urgent

    Execute now.
    """)
    print("Invoice Agent Response:\n", response, "\n")