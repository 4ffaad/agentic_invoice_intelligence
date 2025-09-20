import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { 
  Send, 
  Bot, 
  User, 
  Loader2,
  Sparkles
} from "lucide-react";

interface Message {
  id: string;
  content: string;
  sender: "user" | "ai";
  timestamp: Date;
  type?: "action" | "info" | "warning";
}

const initialMessages: Message[] = [
  {
    id: "1",
    content: "Hello! I'm your ABI assistant. I can help you with billing inquiries, invoice processing, client management, and CRM actions. What would you like me to help you with today?",
    sender: "ai",
    timestamp: new Date(Date.now() - 300000),
    type: "info"
  }
];

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: "user",
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    // Simulate AI response  
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: getAIResponse(inputValue),
        sender: "ai", 
        timestamp: new Date(),
        type: inputValue.toLowerCase().includes("invoice") ? "action" : "info"
      };
      
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const getAIResponse = (input: string): string => {
    const lowerInput = input.toLowerCase();
    
    if (lowerInput.includes("invoice")) {
      return "I can help you with invoice management. I found 3 overdue invoices totaling $45,200. Would you like me to send follow-up emails to these clients automatically?";
    } else if (lowerInput.includes("payment")) {
      return "I've identified $127,000 in pending payments. I can schedule automated reminders and update payment terms. Should I proceed with the standard reminder sequence?";
    } else if (lowerInput.includes("client") || lowerInput.includes("customer")) {
      return "I can access client data and CRM records. What specific client information do you need? I can also create follow-up tasks or schedule communications.";
    } else {
      return "I understand you need assistance with billing operations. I can help with invoice processing, payment tracking, client communications, and generating reports. What specific task would you like me to handle?";
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageTypeColor = (type?: string) => {
    switch (type) {
      case "action":
        return "bg-warning/10 border-l-warning/50";
      case "warning":
        return "bg-destructive/10 border-l-destructive/50";
      default:
        return "bg-accent/5 border-l-accent/30";
    }
  };

  return (
    <Card className="bg-card shadow-card flex flex-col h-[500px]">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-primary-foreground" />
          </div>
          AI Assistant
          <Badge variant="outline" className="bg-success/10 text-success border-success/20 ml-auto">
            Online
          </Badge>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="flex flex-col flex-1 p-0">
        <ScrollArea className="flex-1 px-6">
          <div className="space-y-4 pb-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.sender === "ai" && (
                  <div className="w-6 h-6 bg-accent/20 rounded-full flex items-center justify-center shrink-0 mt-1">
                    <Bot className="w-3 h-3 text-accent" />
                  </div>
                )}
                
                <div
                  className={`max-w-[80%] rounded-lg p-3 border-l-2 ${
                    message.sender === "user"
                      ? "bg-primary/10 border-l-primary/50 text-primary-foreground"
                      : getMessageTypeColor(message.type)
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  <span className="text-xs text-muted-foreground mt-1 block">
                    {message.timestamp.toLocaleTimeString([], { 
                      hour: '2-digit', 
                      minute: '2-digit' 
                    })}
                  </span>
                </div>
                
                {message.sender === "user" && (
                  <div className="w-6 h-6 bg-primary/20 rounded-full flex items-center justify-center shrink-0 mt-1">
                    <User className="w-3 h-3 text-primary" />
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-3">
                <div className="w-6 h-6 bg-accent/20 rounded-full flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-3 h-3 text-accent" />
                </div>
                <div className="bg-accent/5 border-l-2 border-l-accent/30 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 animate-spin text-accent" />
                    <span className="text-sm text-muted-foreground">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
        
        <div className="border-t border-border p-4">
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about invoices, payments, clients..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button 
              onClick={handleSendMessage}
              disabled={isLoading || !inputValue.trim()}
              size="icon"
              className="shrink-0"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}