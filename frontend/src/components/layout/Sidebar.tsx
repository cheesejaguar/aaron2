import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";
import {
  Apple,
  Bot,
  ChefHat,
  Calendar,
  Heart,
  Home,
  Menu,
  Settings,
  ShoppingCart,
  UtensilsCrossed,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { Button } from "@/components/ui/button";

const navItems = [
  { to: "/", icon: Home, label: "Dashboard" },
  { to: "/pantry", icon: Apple, label: "Pantry" },
  { to: "/recipes", icon: ChefHat, label: "Recipes" },
  { to: "/meal-planner", icon: Calendar, label: "Meal Planner" },
  { to: "/shopping", icon: ShoppingCart, label: "Shopping" },
  { to: "/food-log", icon: UtensilsCrossed, label: "Food Log" },
  { to: "/health", icon: Heart, label: "Health" },
  { to: "/coach", icon: Bot, label: "AI Coach" },
];

export function Sidebar() {
  const collapsed = useUIStore((s) => s.sidebarCollapsed);
  const toggle = useUIStore((s) => s.toggleSidebar);

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-border/40 bg-card h-screen sticky top-0 transition-all duration-200",
        collapsed ? "w-16" : "w-56"
      )}
    >
      <div className="flex items-center gap-2 p-4 border-b border-border/40">
        <Button variant="ghost" size="icon" className="h-8 w-8 rounded-lg" onClick={toggle}>
          <Menu className="h-5 w-5" />
        </Button>
        {!collapsed && (
          <span
            className="font-bold text-lg"
            style={{ fontFamily: "'DM Serif Display', serif" }}
          >
            Aaron 2.0
          </span>
        )}
      </div>

      <nav className="flex-1 p-2 space-y-1">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-xl text-sm transition-colors",
                isActive
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground/60 hover:bg-muted/30 hover:text-foreground/80"
              )
            }
          >
            <Icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="p-2 border-t border-border/40">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 px-3 py-2 rounded-xl text-sm transition-colors",
              isActive
                ? "bg-primary/10 text-primary"
                : "text-muted-foreground/60 hover:bg-muted/30 hover:text-foreground/80"
            )
          }
        >
          <Settings className="h-5 w-5 shrink-0" />
          {!collapsed && <span>Settings</span>}
        </NavLink>
      </div>
    </aside>
  );
}
