import { SidebarProvider, SidebarTrigger, SidebarInset } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { Search, User, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex min-h-screen w-full">
        <AppSidebar />
        
        <SidebarInset>
          {/* Header */}
          <header className="h-14 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-40">
            <div className="flex items-center justify-between px-4 sm:px-6 h-full">
              <div className="flex items-center gap-2 sm:gap-4">
                <SidebarTrigger />
                <div className="hidden sm:flex items-center gap-2">
                  <Search className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Search ABI...</span>
                </div>
              </div>
              
              <div className="flex items-center gap-2 sm:gap-3">
                <Button variant="outline" size="sm" className="gap-2 hover:bg-primary hover:text-primary-foreground transition-colors">
                  <Zap className="w-4 h-4" />
                  <span className="hidden sm:inline">Connect Zoho</span>
                </Button>
                
                <Button variant="ghost" size="icon">
                  <User className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 p-4 sm:p-6 bg-gradient-surface">
            {children}
          </main>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}