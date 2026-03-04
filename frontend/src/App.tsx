import { Route, Routes } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AppLayout } from "@/components/layout/AppLayout";
import { CoachPage } from "@/pages/CoachPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { FoodLogPage } from "@/pages/FoodLogPage";
import { HealthMetricsPage } from "@/pages/HealthMetricsPage";
import { MealPlannerPage } from "@/pages/MealPlannerPage";
import { PantryPage } from "@/pages/PantryPage";
import { RecipesPage } from "@/pages/RecipesPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { ShoppingListPage } from "@/pages/ShoppingListPage";

export default function App() {
  return (
    <>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/pantry" element={<PantryPage />} />
          <Route path="/recipes" element={<RecipesPage />} />
          <Route path="/meal-planner" element={<MealPlannerPage />} />
          <Route path="/shopping" element={<ShoppingListPage />} />
          <Route path="/food-log" element={<FoodLogPage />} />
          <Route path="/health" element={<HealthMetricsPage />} />
          <Route path="/coach" element={<CoachPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
      <Toaster />
    </>
  );
}
