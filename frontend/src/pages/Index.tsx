import { DashboardStats } from "@/components/DashboardStats";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TrendingUp, DollarSign, FileText, CheckCircle2 } from "lucide-react";
import heroImage from "@/assets/dashboard-hero.jpg";

const Index = () => {
  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Hero Section */}
      <div className="relative rounded-xl overflow-hidden bg-gradient-primary p-6 sm:p-8 text-primary-foreground">
        <div className="absolute inset-0 opacity-20">
          <img 
            src={heroImage} 
            alt="Dashboard analytics visualization" 
            className="w-full h-full object-cover"
          />
        </div>
        <div className="relative z-10">
          <h1 className="text-2xl sm:text-3xl font-bold mb-2">Welcome to ABI Dashboard</h1>
          <p className="text-primary-foreground/80 text-base sm:text-lg">
            Your Agentic Billing Intelligence is monitoring 247 active invoices and has processed $2.1M this month.
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <DashboardStats />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
        {/* Revenue Analytics */}
        <Card className="bg-gradient-primary text-primary-foreground hover:shadow-glow transition-shadow">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <TrendingUp className="w-5 h-5" />
              Revenue Analytics
            </CardTitle>
            <CardDescription className="text-primary-foreground/80">
              Monthly revenue trends and forecasts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm opacity-90">This Month</span>
                <span className="text-xl sm:text-2xl font-bold">$2.1M</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm opacity-90">Growth</span>
                <Badge variant="secondary" className="bg-white/20 text-white border-white/20">
                  +23.5%
                </Badge>
              </div>
              <div className="pt-2">
                <Button variant="secondary" size="sm" className="w-full bg-white/20 hover:bg-white/30 text-white border-white/20">
                  View Details
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Outstanding Invoices */}
        <Card className="hover:shadow-elegant transition-all duration-300 hover:scale-[1.02]">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <FileText className="w-5 h-5 text-warning" />
              Outstanding Invoices
            </CardTitle>
            <CardDescription>
              Invoices requiring attention
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Total Outstanding</span>
                <span className="text-xl sm:text-2xl font-bold">$847K</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Overdue (30+ days)</span>
                <Badge variant="destructive">$234K</Badge>
              </div>
              <div className="pt-2">
                <Button variant="outline" size="sm" className="w-full">
                  Review Invoices
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="hover:shadow-elegant transition-all duration-300 hover:scale-[1.02] lg:col-span-2 xl:col-span-1">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg">
              <CheckCircle2 className="w-5 h-5 text-success" />
              Recent Activity
            </CardTitle>
            <CardDescription>
              Latest billing activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-success rounded-full flex-shrink-0"></div>
                <span>Invoice #INV-2024-1045 paid</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-primary rounded-full flex-shrink-0"></div>
                <span>3 invoices generated</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <div className="w-2 h-2 bg-warning rounded-full flex-shrink-0"></div>
                <span>Follow-up sent to client</span>
              </div>
              <div className="pt-2">
                <Button variant="ghost" size="sm" className="w-full">
                  View All Activity
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Integration Status */}
      <Card className="bg-gradient-surface border-2 border-dashed border-border hover:border-primary/50 transition-colors">
        <CardContent className="flex flex-col sm:flex-row items-center justify-between p-4 sm:p-6 gap-4">
          <div className="text-center sm:text-left">
            <h3 className="text-lg font-semibold mb-1">Connect Your Business Systems</h3>
            <p className="text-muted-foreground text-sm">
              Integrate with Zoho CRM and accounting software to unlock the full potential of ABI
            </p>
          </div>
          <div className="flex gap-3 flex-shrink-0">
            <Button className="gap-2 hover:shadow-glow transition-shadow">
              <DollarSign className="w-4 h-4" />
              <span className="hidden sm:inline">Connect</span> Zoho
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Index;
