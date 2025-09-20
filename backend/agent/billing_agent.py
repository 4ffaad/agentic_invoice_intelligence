# billing_agent.py
import os
from dotenv import load_dotenv
from strands import Agent
from strands.models import BedrockModel
from invoice_tools import (
    get_invoice_details, 
    list_all_invoices,
    get_overdue_invoices,
    update_invoice_status,
    get_customer_invoice_history
)
from memory_hooks import CustomerSupportMemoryHooks, create_memory_client, create_memory_resource

# Load environment variables
load_dotenv()

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

# Create memory client and resource
memory_client = create_memory_client()
memory_id = create_memory_resource(memory_client)

# Create memory hooks for this customer session
customer_id = "CUST-001"
session_id = "session-001"
memory_hooks = CustomerSupportMemoryHooks(
    memory_id=memory_id,
    client=memory_client,
    actor_id=customer_id,
    session_id=session_id
)

# Create the billing agent with memory capabilities
billing_agent = Agent(
    model=bedrock_model,
    system_prompt=BILLING_AGENT_PROMPT,
    tools=[
        get_invoice_details,
        list_all_invoices, 
        get_overdue_invoices,
        update_invoice_status,
        get_customer_invoice_history
    ],
    hooks=[memory_hooks]
)

# Test scenarios
if __name__ == "__main__":
    print("🚀 PayPilot Agentic Invoice Intelligence - With AgentCore Memory")
    print("=" * 70)
    print("📝 Testing persistent memory and hyper-personalized responses")
    print("=" * 70)
    
    # Test personalized recommendations
    print("\n" + "=" * 60)
    print("TEST 1: Personalized Recommendations")
    print("=" * 60)
    response1 = billing_agent("Which headphones would you recommend?")
    # Agent remembers: "prefers low latency for competitive FPS games"
    # Response includes gaming-focused recommendations
    print(f"Agent: {response1}\n")
    
    # Test preference recall
    print("=" * 60)
    print("TEST 2: Preference Recall")
    print("=" * 60)
    response2 = billing_agent("What is my preferred laptop brand?")
    # Agent remembers: "prefers ThinkPad models" and "needs Linux compatibility"
    # Response acknowledges ThinkPad preference and suggests compatible models
    print(f"Agent: {response2}\n")
    
    # Test billing-specific memory
    print("=" * 60)
    print("TEST 3: Billing Memory Test")
    print("=" * 60)
    response3 = billing_agent("I prefer to pay invoices via bank transfer and need 30-day payment terms. Can you help me with my billing?")
    print(f"Agent: {response3}\n")
    
    # Test memory recall for billing preferences
    print("=" * 60)
    print("TEST 4: Billing Preference Recall")
    print("=" * 60)
    response4 = billing_agent("What are my preferred payment terms and method?")
    print(f"Agent: {response4}\n")
    
    print("=" * 70)
    print("Memory-Enhanced Agent Test Completed!")
    print("=" * 70)
    print("Agent now has persistent memory across conversations")
    print("Customer preferences are remembered and applied")
    print("Context-aware responses based on previous interactions")