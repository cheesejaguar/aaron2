import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { CoachPanel } from "./CoachPanel";
import { useUIStore } from "@/stores/ui-store";
import { cn } from "@/lib/utils";

export function AppLayout() {
  const coachOpen = useUIStore((s) => s.coachPanelOpen);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet />
      </main>
      <div
        className={cn(
          "border-l border-border bg-card transition-all duration-200 overflow-hidden",
          coachOpen ? "w-96" : "w-0"
        )}
      >
        {coachOpen && <CoachPanel />}
      </div>
    </div>
  );
}
