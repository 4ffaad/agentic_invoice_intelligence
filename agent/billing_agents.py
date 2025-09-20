# billing_agent.py
from strands import Agent
from strands.models import BedrockModel
from invoice_tools import (
    get_invoice_details, 
    list_all_invoices,
    get_overdue_invoices,
    update_invoice_status,
    get_customer_invoice_history
)

# Create Bedrock model
bedrock_model = BedrockModel(
    model_id="us.amazon.nova-lite-v1:0",
    temperature=0.3
)

# Enhanced system prompt
BILLING_AGENT_PROMPT = """
You are an intelligent billing agent for a SaaS company. You have access to the company's invoice management system and can perform all billing operations autonomously.

AVAILABLE INVOICE OPERATIONS:
- create_invoice: Create new invoices for customers
- get_invoice_details: Get detailed info about specific invoices
- list_all_invoices: Get all invoices (can filter by status)
- get_overdue_invoices: Get invoices that need immediate attention
- update_invoice_status: Mark invoices as paid, cancelled, etc.
- get_customer_invoice_history: Analyze customer payment patterns

DECISION FRAMEWORK FOR OVERDUE INVOICES:
- 1-7 days overdue: Monitor, prepare gentle reminder
- 8-21 days overdue: Send firm reminder, flag for attention
- 22+ days overdue: Escalate to finance team immediately

CUSTOMER RELATIONSHIP MANAGEMENT:
- Always check customer payment history before taking action
- Good payment history = more patience and gentle approach
- Poor payment history = faster escalation and firmer tone
- New customers = educational and supportive approach

AUTONOMOUS OPERATIONS:
- When asked to "handle overdue accounts", you should:
  1. Get all overdue invoices
  2. Check each customer's payment history  
  3. Take appropriate action based on days overdue and history
  4. Provide summary of actions taken

- When asked to "process billing", you should:
  1. Review all pending invoices
  2. Identify any issues or patterns
  3. Take proactive measures
  4. Report findings and recommendations

Always be professional, data-driven, and focused on maintaining good customer relationships while optimizing cash flow.
"""

# Create the billing agent
billing_agent = Agent(
    model=bedrock_model,
    system_prompt=BILLING_AGENT_PROMPT,
    tools=[
        get_invoice_details,
        list_all_invoices, 
        get_overdue_invoices,
        update_invoice_status,
        get_customer_invoice_history
    ]
)

# Test scenarios
if __name__ == "__main__":
    print("Testing Billing Agent with Your Lambda Functions\n")
    
    # # Test 1: Check current overdue situation
    # print("=" * 60)
    # print("TEST 1: Overdue Invoice Analysis")
    # print("=" * 60)
    # response1 = billing_agent("Please analyze all overdue invoices and tell me what actions we should take for each.")
    # print(f"Agent: {response1}\n")
    
    # Test 2: Customer-specific analysis
    print("=" * 60)
    print("TEST 2: Customer Payment Analysis")
    print("=" * 60)
    response2 = billing_agent("Check the payment history for customer CUST-001 and assess their risk level.")
    print(f"Agent: {response2}\n")
    
    # # Test 3: Autonomous billing management
    # print("=" * 60)
    # print("TEST 3: Autonomous Billing Management") 
    # print("=" * 60)
    # response3 = billing_agent("Handle all overdue accounts autonomously. Take appropriate action for each based on how overdue they are and their payment history.")
    # print(f"Agent: {response3}\n")