import { AIChat } from "@/components/AIChat";

const Chat = () => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-foreground mb-2">AI Assistant</h1>
        <p className="text-muted-foreground">
          Chat with your Agentic Billing Intelligence to request actions, get insights, and manage your billing processes.
        </p>
      </div>
      <AIChat />
    </div>
  );
};

export default Chat;