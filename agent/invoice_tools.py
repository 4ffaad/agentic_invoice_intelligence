# tools/invoice_tools.py
from strands import tool
import boto3
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Initialize AWS Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')

# Your API Gateway base URL
API_BASE_URL = "https://1epz8gbc84.execute-api.ap-southeast-5.amazonaws.com/dev"

@tool
def get_invoice_details(invoice_id: str) -> dict:
    """Get detailed information about a specific invoice including payment status and overdue calculations"""
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/invoices/{invoice_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            invoice = result["invoice"]
            
            return {
                "success": True,
                "invoice_id": invoice["invoiceId"],
                "customer_id": invoice["customerId"],
                "deal_id": invoice.get("dealId"),
                "customer_name": invoice["name"],
                "customer_email": invoice["email"],
                "company_name": invoice["companyName"],
                "amount": invoice["amount"],
                "currency": invoice.get("currency", "MYR"),
                "status": invoice["status"],
                "due_date": invoice["dueDate"],
                "created_at": invoice["createdAt"],
                "is_overdue": invoice.get("isOverdue", False),
                "days_overdue": invoice.get("daysOverdue", 0),
                "email_sent": invoice.get("emailSent", False),
                "payment_terms": invoice.get("paymentTerms", "Due on receipt"),
                "language": invoice.get("language", "en"),
                "timezone": invoice.get("timezone", "Asia/Kuala_Lumpur"),
                "line_items": invoice.get("lineItems", []),
                "s3_key": invoice.get("s3Key")
            }
        else:
            return {
                "success": False,
                "error": f"Invoice {invoice_id} not found"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting invoice: {str(e)}"
        }

@tool
def list_all_invoices(status_filter: Optional[str] = None) -> dict:
    """Get list of all invoices, optionally filtered by status (sent, paid)"""
    
    try:
        url = f"{API_BASE_URL}/invoices"
        if status_filter:
            url += f"?status={status_filter}"
            
        response = requests.get(
            url,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            processed_invoices = []
            for invoice in result["invoices"]:
                processed_invoices.append({
                    "invoice_id": invoice["invoiceId"],
                    "customer_id": invoice["customerId"],
                    "deal_id": invoice.get("dealId"),
                    "customer_name": invoice["name"],
                    "customer_email": invoice["email"],
                    "company_name": invoice["companyName"],
                    "amount": invoice["amount"],
                    "currency": invoice.get("currency", "MYR"),
                    "status": invoice["status"],
                    "due_date": invoice["dueDate"],
                    "created_at": invoice["createdAt"],
                    "is_overdue": invoice.get("isOverdue", False),
                    "days_overdue": invoice.get("daysOverdue", 0),
                    "email_sent": invoice.get("emailSent", False),
                    "payment_terms": invoice.get("paymentTerms")
                })
            
            return {
                "success": True,
                "summary": result["summary"],
                "total_invoices": len(processed_invoices),
                "overdue_invoices": [inv for inv in processed_invoices if inv["is_overdue"]],
                "sent_invoices": [inv for inv in processed_invoices if inv["status"] == "sent"],
                "paid_invoices": [inv for inv in processed_invoices if inv["status"] == "paid"],
                "all_invoices": processed_invoices
            }
        else:
            return {
                "success": False,
                "error": f"Failed to list invoices: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error listing invoices: {str(e)}"
        }

@tool
def get_overdue_invoices() -> dict:
    """Get all overdue invoices that need attention (status='sent' and past due date)"""
    
    try:
        # Get all sent invoices
        all_invoices = list_all_invoices("sent")
        
        if not all_invoices["success"]:
            return all_invoices
        
        # Filter for overdue ones
        overdue_invoices = []
        for invoice in all_invoices["all_invoices"]:
            if invoice["is_overdue"]:
                overdue_invoices.append(invoice)
        
        # Sort by days overdue (most urgent first)
        overdue_invoices.sort(key=lambda x: x["days_overdue"], reverse=True)
        
        # Categorize by urgency
        urgent_invoices = [inv for inv in overdue_invoices if inv["days_overdue"] > 21]
        moderate_invoices = [inv for inv in overdue_invoices if 8 <= inv["days_overdue"] <= 21]
        recent_invoices = [inv for inv in overdue_invoices if inv["days_overdue"] <= 7]
        
        return {
            "success": True,
            "overdue_count": len(overdue_invoices),
            "total_overdue_amount": sum(inv["amount"] for inv in overdue_invoices),
            "overdue_invoices": overdue_invoices,
            "urgent_invoices": urgent_invoices,  # 22+ days
            "moderate_invoices": moderate_invoices,  # 8-21 days
            "recent_invoices": recent_invoices  # 1-7 days
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting overdue invoices: {str(e)}"
        }

@tool
def update_invoice_status(invoice_id: str) -> dict:
    """Mark an invoice as paid with automatic DynamoDB and Zoho synchronization"""
    
    try:
        # Make PUT request to /invoices/{invoice_id} endpoint
        # The invoice_id goes in the URL path, no body needed
        response = requests.put(
            f"{API_BASE_URL}/invoices/{invoice_id}",  # invoice_id in path
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "invoice_id": invoice_id,
                "status": "paid",
                "message": result.get("message", f"Invoice {invoice_id} marked as paid"),
                "invoice": result.get("invoice", {}),
                "dynamodb_updated": True,
                "zoho_updated": True,
                "zoho_response": result.get("zoho_response", {})
            }
        else:
            return {
                "success": False,
                "error": f"Failed to mark invoice as paid: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error marking invoice as paid: {str(e)}"
        }

@tool 
def get_customer_invoice_history(customer_id: str) -> dict:
    """Get all invoices for a specific customer to analyze payment patterns"""
    
    try:
        # Get all invoices and filter by customer
        all_invoices = list_all_invoices()
        
        if not all_invoices["success"]:
            return all_invoices
        
        customer_invoices = [
            inv for inv in all_invoices["all_invoices"] 
            if inv["customer_id"] == customer_id
        ]
        
        if not customer_invoices:
            return {
                "success": True,
                "customer_id": customer_id,
                "total_invoices": 0,
                "message": "No invoices found for this customer"
            }
        
        # Analyze payment patterns
        total_invoices = len(customer_invoices)
        paid_invoices = [inv for inv in customer_invoices if inv["status"] == "paid"]
        sent_invoices = [inv for inv in customer_invoices if inv["status"] == "sent"]
        overdue_invoices = [inv for inv in customer_invoices if inv["is_overdue"]]
        
        total_amount = sum(inv["amount"] for inv in customer_invoices)
        paid_amount = sum(inv["amount"] for inv in paid_invoices)
        overdue_amount = sum(inv["amount"] for inv in overdue_invoices)
        
        # Calculate payment rate
        payment_rate = len(paid_invoices) / total_invoices if total_invoices > 0 else 0
        
        # Determine risk level
        if payment_rate >= 0.9:
            risk_level = "LOW"
        elif payment_rate >= 0.7:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        # Get customer details from first invoice
        customer_info = customer_invoices[0]
        
        return {
            "success": True,
            "customer_id": customer_id,
            "customer_name": customer_info["customer_name"],
            "customer_email": customer_info["customer_email"],
            "company_name": customer_info["company_name"],
            "total_invoices": total_invoices,
            "paid_invoices": len(paid_invoices),
            "sent_invoices": len(sent_invoices),
            "overdue_invoices": len(overdue_invoices),
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "overdue_amount": overdue_amount,
            "payment_rate": payment_rate,
            "risk_level": risk_level,
            "currency": customer_info.get("currency", "MYR"),
            "language": customer_info.get("language", "en"),
            "timezone": customer_info.get("timezone", "Asia/Kuala_Lumpur"),
            "invoices": customer_invoices
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting customer history: {str(e)}"
        }
    
@tool
def send_personalized_email(customer_name: str, 
                          invoice_number: str, amount: float, 
                          days_overdue: int, customer_history: str = "",
                          ai_generated_content: dict = None) -> dict:
    """Send AI-personalized email via API Gateway"""
    
    # Calculate due date
    from datetime import datetime, timedelta
    if days_overdue > 0:
        due_date = (datetime.now() - timedelta(days=days_overdue)).strftime("%Y-%m-%d")
    else:
        due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Use AI-generated content if provided, otherwise create basic content
    if ai_generated_content:
        subject = ai_generated_content.get("subject", f"Invoice {invoice_number}")
        body = ai_generated_content.get("body", "Please review your invoice.")
        tone = ai_generated_content.get("tone", "professional")
        personalization_notes = ai_generated_content.get("personalization_notes", "")
    else:
        if days_overdue == 0:
            tone = "professional"
            subject = f"Invoice {invoice_number}"
            body = f"Please find your invoice {invoice_number} for ${amount}."
        elif days_overdue <= 7:
            tone = "gentle"
            subject = f"Friendly Reminder: Invoice {invoice_number}"
            body = f"Gentle reminder for invoice {invoice_number} (${amount}, {days_overdue} days overdue)."
        else:
            tone = "urgent"
            subject = f"Urgent: Invoice {invoice_number}"
            body = f"Invoice {invoice_number} is {days_overdue} days overdue. Immediate attention required."
        
        personalization_notes = f"Based on: {customer_history}"
    
    # Prepare API request payload
    payload = {
        "customer_email": "kenzierivan263@gmail.com",
        "customer_name": customer_name,
        "invoice_number": invoice_number,
        "amount": str(amount),
        "due_date": due_date,
        "invoice_url": f"https://invoice-storage.s3.amazonaws.com/{invoice_number}.pdf",
        "days_overdue": days_overdue,
        "ai_generated_content": {
            "subject": subject,
            "body": body,
            "tone": tone,
            "personalization_notes": personalization_notes
        }
    }
    
    # Call API Gateway endpoint
    try:
        import requests
        
        response = requests.post(
            f"{API_BASE_URL}/send-email",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "message": f"Personalized {tone} email sent to {customer_name}",
                "details": result
            }
        else:
            return {
                "success": False,
                "error": f"API call failed: {response.status_code} - {response.text}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to call API: {str(e)}"
        }
    
@tool
def get_customer_id_from_invoice(invoice_id: str) -> dict:
    """Get customer ID from an invoice ID"""
    
    try:
        # Use existing get_invoice_details function
        invoice_result = get_invoice_details(invoice_id)
        
        if invoice_result["success"]:
            return {
                "success": True,
                "invoice_id": invoice_id,
                "customer_id": invoice_result["customer_id"],
                "customer_name": invoice_result["customer_name"],
                "customer_email": invoice_result["customer_email"],
                "company_name": invoice_result["company_name"]
            }
        else:
            return {
                "success": False,
                "error": f"Invoice {invoice_id} not found"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting customer ID: {str(e)}"
        }