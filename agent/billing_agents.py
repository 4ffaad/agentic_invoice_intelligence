# billing_agent.py
from strands import Agent, tool
from strands.models import BedrockModel
from invoice_tools import (
    get_invoice_details, 
    list_all_invoices,
    get_overdue_invoices,
    update_invoice_status,
    get_customer_invoice_history,
    send_personalized_email
)

# Create Bedrock model
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    temperature=0.3
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

PERSONALIZATION EXAMPLES:

For reliable customer (5 days overdue):
- subject: "Friendly reminder: Invoice INV-001 - We value your partnership"
- body: "Hi [Name], I hope you're doing well. As one of our valued clients with excellent payment history, I wanted to reach out about invoice INV-001. I know how busy things can get, and this may have simply slipped through the cracks..."
- tone: "gentle"

For problematic customer (25 days overdue):
- subject: "Urgent: Invoice INV-002 requires immediate attention"
- body: "Our records show invoice INV-002 for $[amount] is now 25 days overdue. Given the payment history on this account, immediate payment is required to avoid further collection actions..."
- tone: "urgent"

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

RISK LEVELS:
- LOW (>90% payment rate): Gentle, relationship-focused approach
- MEDIUM (70-90% payment rate): Professional, direct communication  
- HIGH (<70% payment rate): Firm, consequence-focused messaging

ANALYSIS FORMAT:
- Risk score (0-100) with justification
- Payment behavior summary
- Recommended communication tone
- Specific next steps

Always provide data-driven insights with clear recommendations for customer management.

TOOLS: get_customer_invoice_history, list_all_invoices, get_overdue_invoices
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

TOOLS: get_invoice_details, update_invoice_status, list_all_invoices
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
    tools=[get_customer_invoice_history, list_all_invoices, get_overdue_invoices]
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
    tools=[call_analysis_agent, call_email_agent, call_invoice_agent]
)

# Test scenarios
if __name__ == "__main__":
    print("Testing Billing Agent with Your Lambda Functions\n")
    response = invoice_agent("update the status of invoice 7273232000000105054 to 'paid'.")
    print("Invoice Agent Response:\n", response, "\n")