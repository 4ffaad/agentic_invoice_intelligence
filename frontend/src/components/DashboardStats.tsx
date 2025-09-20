import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Activity, CheckCircle, Clock, DollarSign } from "lucide-react";

const stats = [
  {
    title: "Agent Efficiency",
    value: "94.2%",
    change: "+2.1%",
    trend: "up",
    icon: Activity,
    description: "Task completion rate"
  },
  {
    title: "Revenue Processed",
    value: "$1.2M",
    change: "+12.3%", 
    trend: "up",
    icon: DollarSign,
    description: "This month"
  },
  {
    title: "Tasks Completed",
    value: "1,247",
    change: "+8.7%",
    trend: "up", 
    icon: CheckCircle,
    description: "Last 30 days"
  },
  {
    title: "Avg Response Time",
    value: "2.3s",
    change: "-0.8s",
    trend: "up",
    icon: Clock,
    description: "AI agent response"
  }
];

export function DashboardStats() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat) => {
        const Icon = stat.icon;
        const TrendIcon = stat.trend === "up" ? TrendingUp : TrendingDown;
        
        return (
          <Card key={stat.title} className="bg-card shadow-card hover:shadow-elegant transition-smooth">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {stat.title}
              </CardTitle>
              <Icon className="h-4 w-4 text-accent" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{stat.value}</div>
              <div className="flex items-center gap-1 mt-1">
                <TrendIcon className={`h-3 w-3 ${stat.trend === 'up' ? 'text-success' : 'text-destructive'}`} />
                <span className={`text-xs font-medium ${stat.trend === 'up' ? 'text-success' : 'text-destructive'}`}>
                  {stat.change}
                </span>
                <span className="text-xs text-muted-foreground ml-1">
                  {stat.description}
                </span>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}