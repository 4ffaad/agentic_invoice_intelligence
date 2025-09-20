"""
AgentCore Memory Hooks for Billing Agent
"""

from strands.hooks import HookProvider, MessageAddedEvent, AfterInvocationEvent
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.constants import StrategyType


class CustomerSupportMemoryHooks(HookProvider):
    """Memory hooks for customer support agent to provide persistent conversation context"""
    
    def __init__(self, memory_id: str, client: MemoryClient, actor_id: str, session_id: str):
        self.memory_id = memory_id
        self.client = client
        self.actor_id = actor_id
        self.session_id = session_id
        
        # Define namespaces for different memory types
        self.namespaces = {
            "preferences": f"support/customer/{actor_id}/preferences",
            "semantic": f"support/customer/{actor_id}/semantic"
        }
    
    def retrieve_customer_context(self, event: MessageAddedEvent):
        """Inject customer context before processing queries"""
        user_query = event.agent.messages[-1]["content"][0]["text"]
        
        # Retrieve relevant memories from both strategies
        all_context = []
        for context_type, namespace in self.namespaces.items():
            try:
                memories = self.client.retrieve_memories(
                    memory_id=self.memory_id,
                    namespace=namespace,
                    query=user_query,
                    top_k=3,
                )
                # Format and add to context
                for memory in memories:
                    if memory.get("content", {}).get("text"):
                        all_context.append(f"[{context_type.upper()}] {memory['content']['text']}")
            except Exception as e:
                print(f"Warning: Could not retrieve memories from {namespace}: {e}")
        
        # Inject context into the user query
        if all_context:
            context_text = "\n".join(all_context)
            original_text = event.agent.messages[-1]["content"][0]["text"]
            event.agent.messages[-1]["content"][0]["text"] = f"Customer Context:\n{context_text}\n\n{original_text}"
    
    def save_support_interaction(self, event: AfterInvocationEvent):
        """Save interactions after agent responses"""
        try:
            # Get last customer query and agent response
            if len(event.agent.messages) >= 2:
                customer_query = event.agent.messages[-2]["content"][0]["text"]
                agent_response = event.agent.messages[-1]["content"][0]["text"]
                
                # Save to memory for future retrieval
                self.client.create_event(
                    memory_id=self.memory_id,
                    actor_id=self.actor_id,
                    session_id=self.session_id,
                    messages=[(customer_query, "USER"), (agent_response, "ASSISTANT")]
                )
        except Exception as e:
            print(f"Warning: Could not save interaction to memory: {e}")


def create_memory_client(region: str = "us-east-1") -> MemoryClient:
    """Create and configure memory client"""
    return MemoryClient(region_name=region)


def create_memory_resource(client: MemoryClient, name: str = "CustomerSupportMemory") -> str:
    """Create memory resource with customer support strategies"""
    
    strategies = [
        {
            StrategyType.USER_PREFERENCE.value: {
                "name": "CustomerPreferences",
                "description": "Captures customer preferences and behavior",
                "namespaces": ["support/customer/{actorId}/preferences"],
            }
        },
        {
            StrategyType.SEMANTIC.value: {
                "name": "CustomerSupportSemantic", 
                "description": "Stores facts from conversations",
                "namespaces": ["support/customer/{actorId}/semantic"],
            }
        },
    ]
    
    try:
        # Try to create memory resource with both strategies
        response = client.create_memory_and_wait(
            name=name,
            description="Customer support agent memory",
            strategies=strategies,
            event_expiry_days=90,
        )
        return response["memoryId"]
    except Exception as e:
        if "already exists" in str(e) or "Memory with name" in str(e):
            # Memory already exists, try to get existing memory
            try:
                memories = client.list_memories()
                for memory in memories.get("memories", []):
                    if memory.get("name") == name:
                        print(f"Using existing memory: {memory['memoryId']}")
                        return memory["memoryId"]
            except Exception as list_error:
                print(f"Could not list memories: {list_error}")
            # If we can't find existing memory, create with timestamp
            import time
            timestamp = int(time.time())
            new_name = f"{name}_{timestamp}"
            print(f"Creating new memory with name: {new_name}")
            response = client.create_memory_and_wait(
                name=new_name,
                description="Customer support agent memory",
                strategies=strategies,
                event_expiry_days=90,
            )
            return response["memoryId"]
        else:
            raise e
