import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Mail, 
  Phone, 
  FileText, 
  CreditCard, 
  AlertTriangle,
  CheckCircle,
  Clock
} from "lucide-react";

const recentActions = [
  {
    id: 1,
    action: "Follow-up email sent",
    target: "Invoice #INV-2024-0542",
    status: "completed",
    timestamp: "2 minutes ago",
    icon: Mail,
    priority: "normal"
  },
  {
    id: 2,
    action: "Payment reminder scheduled",
    target: "Client: TechCorp Solutions",
    status: "scheduled",
    timestamp: "5 minutes ago", 
    icon: Clock,
    priority: "high"
  },
  {
    id: 3,
    action: "Credit check initiated",
    target: "New client onboarding",
    status: "in-progress",
    timestamp: "8 minutes ago",
    icon: CreditCard,
    priority: "normal"
  },
  {
    id: 4,
    action: "Overdue notice generated",
    target: "Invoice #INV-2024-0538",
    status: "completed",
    timestamp: "12 minutes ago",
    icon: AlertTriangle,
    priority: "urgent"
  },
  {
    id: 5,
    action: "Contract review completed",
    target: "Service Agreement #SA-2024-089",
    status: "completed", 
    timestamp: "15 minutes ago",
    icon: FileText,
    priority: "normal"
  },
  {
    id: 6,
    action: "Payment processed",
    target: "$15,450.00 - Invoice #INV-2024-0540",
    status: "completed",
    timestamp: "18 minutes ago",
    icon: CheckCircle,
    priority: "normal"
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "completed":
      return "bg-success/10 text-success border-success/20";
    case "in-progress":
      return "bg-warning/10 text-warning border-warning/20";
    case "scheduled":
      return "bg-accent/10 text-accent border-accent/20";
    default:
      return "bg-muted text-muted-foreground";
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case "urgent":
      return "bg-destructive/10 text-destructive border-destructive/20";
    case "high":
      return "bg-warning/10 text-warning border-warning/20";
    default:
      return "bg-muted/50 text-muted-foreground border-muted";
  }
};

export function AgentActions() {
  return (
    <Card className="bg-card shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
          Recent Agent Actions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-4">
            {recentActions.map((action) => {
              const Icon = action.icon;
              
              return (
                <div key={action.id} className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/30 transition-smooth">
                  <div className="w-8 h-8 bg-accent/10 rounded-lg flex items-center justify-center shrink-0">
                    <Icon className="w-4 h-4 text-accent" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-medium text-sm text-foreground">{action.action}</p>
                      <Badge variant="outline" className={getPriorityColor(action.priority)}>
                        {action.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{action.target}</p>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className={getStatusColor(action.status)}>
                        {action.status}
                      </Badge>
                      <span className="text-xs text-muted-foreground">{action.timestamp}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}