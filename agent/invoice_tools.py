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
def get_invoice_details(invoice_id: str) -> Dict:
    """Get detailed information about a specific invoice"""
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/invoices/{invoice_id}",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            invoice = result["invoice"]
            
            # Calculate if overdue
            due_date = datetime.fromisoformat(invoice["dueDate"].replace('Z', '+00:00'))
            days_overdue = (datetime.now(due_date.tzinfo) - due_date).days
            is_overdue = days_overdue > 0 and invoice["status"] == "pending"
            
            return {
                "success": True,
                "invoice_id": invoice["invoiceId"],
                "customer_id": invoice["customerId"],
                "customer_name": invoice["customerName"],
                "amount": invoice["amount"],
                "status": invoice["status"],
                "due_date": invoice["dueDate"],
                "created_date": invoice["createdDate"],
                "is_overdue": is_overdue,
                "days_overdue": max(0, days_overdue),
                "description": invoice.get("description", "")
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
def list_all_invoices(status_filter: Optional[str] = None) -> Dict:
    """Get list of all invoices, optionally filtered by status"""
    
    try:
        url = f"{API_BASE_URL}/invoices"
        if status_filter:
            url += f"?status={status_filter}"
            
        response = requests.get(
            url,
            headers={
                "Content-Type": "application/json",
                "x-user-id": "agent-system"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Process invoices to add overdue information
            processed_invoices = []
            for invoice in result["invoices"]:
                due_date = datetime.fromisoformat(invoice["dueDate"].replace('Z', '+00:00'))
                days_overdue = (datetime.now(due_date.tzinfo) - due_date).days
                is_overdue = days_overdue > 0 and invoice["status"] == "pending"
                
                processed_invoices.append({
                    "invoice_id": invoice["invoiceId"],
                    "customer_id": invoice["customerId"], 
                    "customer_name": invoice["customerName"],
                    "amount": invoice["amount"],
                    "status": invoice["status"],
                    "due_date": invoice["dueDate"],
                    "is_overdue": is_overdue,
                    "days_overdue": max(0, days_overdue)
                })
            
            return {
                "success": True,
                "summary": result["summary"],
                "total_invoices": len(processed_invoices),
                "overdue_invoices": [inv for inv in processed_invoices if inv["is_overdue"]],
                "pending_invoices": [inv for inv in processed_invoices if inv["status"] == "pending"],
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
def get_overdue_invoices() -> Dict:
    """Get all overdue invoices that need attention"""
    
    try:
        # Get all pending invoices
        all_invoices = list_all_invoices("pending")
        
        if not all_invoices["success"]:
            return all_invoices
        
        # Filter for overdue ones
        overdue_invoices = []
        for invoice in all_invoices["all_invoices"]:
            if invoice["is_overdue"]:
                overdue_invoices.append(invoice)
        
        # Sort by days overdue (most urgent first)
        overdue_invoices.sort(key=lambda x: x["days_overdue"], reverse=True)
        
        return {
            "success": True,
            "overdue_count": len(overdue_invoices),
            "total_overdue_amount": sum(inv["amount"] for inv in overdue_invoices),
            "overdue_invoices": overdue_invoices,
            "urgent_invoices": [inv for inv in overdue_invoices if inv["days_overdue"] > 21],
            "moderate_invoices": [inv for inv in overdue_invoices if 8 <= inv["days_overdue"] <= 21],
            "recent_invoices": [inv for inv in overdue_invoices if inv["days_overdue"] <= 7]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting overdue invoices: {str(e)}"
        }

@tool
def update_invoice_status(invoice_id: str, new_status: str, notes: Optional[str] = None) -> Dict:
    """Update an invoice status (pending, paid, cancelled, etc.)"""
    
    payload = {
        "status": new_status
    }
    
    if notes:
        payload["notes"] = notes
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/invoices/{invoice_id}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "invoice_id": invoice_id,
                "new_status": new_status,
                "updated_invoice": result["invoice"]
            }
        else:
            return {
                "success": False,
                "error": f"Failed to update invoice: {response.text}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error updating invoice: {str(e)}"
        }

@tool 
def get_customer_invoice_history(customer_id: str) -> Dict:
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
        overdue_invoices = [inv for inv in customer_invoices if inv["is_overdue"]]
        
        total_amount = sum(inv["amount"] for inv in customer_invoices)
        overdue_amount = sum(inv["amount"] for inv in overdue_invoices)
        
        return {
            "success": True,
            "customer_id": customer_id,
            "customer_name": customer_invoices[0]["customer_name"],
            "total_invoices": total_invoices,
            "paid_invoices": len(paid_invoices),
            "overdue_invoices": len(overdue_invoices),
            "total_amount": total_amount,
            "overdue_amount": overdue_amount,
            "payment_rate": len(paid_invoices) / total_invoices if total_invoices > 0 else 0,
            "risk_level": "HIGH" if len(overdue_invoices) > 2 else "MEDIUM" if len(overdue_invoices) > 0 else "LOW",
            "invoices": customer_invoices
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error getting customer history: {str(e)}"
        }