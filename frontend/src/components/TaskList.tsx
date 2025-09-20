import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  CheckCircle, 
  Clock, 
  AlertTriangle, 
  FileText,
  DollarSign,
  User,
  Phone
} from "lucide-react";

const tasks = [
  {
    id: 1,
    title: "Review overdue invoice #INV-2024-0532",
    description: "Client: ABC Manufacturing - $24,500.00 - 15 days overdue",
    priority: "urgent",
    type: "invoice",
    dueDate: "Today",
    icon: AlertTriangle
  },
  {
    id: 2,
    title: "Approve credit extension request",
    description: "TechCorp Solutions requesting $50,000 credit increase",
    priority: "high",
    type: "approval",
    dueDate: "Tomorrow",
    icon: DollarSign
  },
  {
    id: 3,
    title: "Call client about payment terms",
    description: "Global Industries - Negotiate new payment schedule",
    priority: "medium",
    type: "communication",
    dueDate: "This week",
    icon: Phone
  },
  {
    id: 4,
    title: "Update customer information",
    description: "Metro Systems - Address and contact details need updating",
    priority: "low",
    type: "data",
    dueDate: "Next week",
    icon: User
  },
  {
    id: 5,
    title: "Generate monthly report",
    description: "Billing summary for November 2024",
    priority: "medium", 
    type: "report",
    dueDate: "Dec 5",
    icon: FileText
  }
];

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case "urgent":
      return "bg-destructive/10 text-destructive border-destructive/20";
    case "high":
      return "bg-warning/10 text-warning border-warning/20";
    case "medium":
      return "bg-accent/10 text-accent border-accent/20";
    default:
      return "bg-muted/50 text-muted-foreground border-muted";
  }
};

export function TaskList() {
  return (
    <Card className="bg-card shadow-card">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Priority Tasks</span>
          <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
            {tasks.length} pending
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-4">
            {tasks.map((task) => {
              const Icon = task.icon;
              
              return (
                <div key={task.id} className="p-4 rounded-lg border border-border hover:bg-muted/30 transition-smooth">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-muted rounded-lg flex items-center justify-center shrink-0">
                      <Icon className="w-4 h-4 text-muted-foreground" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <h4 className="font-medium text-sm text-foreground leading-tight">
                          {task.title}
                        </h4>
                        <Badge variant="outline" className={getPriorityColor(task.priority)}>
                          {task.priority}
                        </Badge>
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
                        {task.description}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          Due {task.dueDate}
                        </div>
                        
                        <Button size="sm" variant="outline" className="h-7 text-xs">
                          Take Action
                        </Button>
                      </div>
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