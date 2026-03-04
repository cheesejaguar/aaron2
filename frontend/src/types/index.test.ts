import { describe, it, expect } from "vitest";
import type {
  User,
  PantryItem,
  FoodLog,
  BPLog,
  DashboardData,
  MealPlan,
  ShoppingList,
} from "./index";

describe("TypeScript interfaces", () => {
  it("User interface has required fields", () => {
    const user: User = { id: "1", email: "test@test.com", name: "Test" };
    expect(user.id).toBe("1");
    expect(user.email).toBe("test@test.com");
  });

  it("PantryItem supports optional fields", () => {
    const item: PantryItem = {
      id: "1",
      name: "Milk",
      quantity: 2,
      category: "dairy",
      unit: "gallons",
    };
    expect(item.name).toBe("Milk");
    expect(item.quantity).toBe(2);
  });

  it("FoodLog with macros", () => {
    const log: FoodLog = {
      id: "1",
      logged_at: "2025-06-15T12:00:00Z",
      meal_type: "lunch",
      food_name: "Salad",
      calories: 300,
      protein_g: 20,
      carbs_g: 30,
      fat_g: 10,
    };
    expect(log.food_name).toBe("Salad");
    expect(log.calories).toBe(300);
  });

  it("BPLog with optional fields", () => {
    const log: BPLog = {
      id: "1",
      systolic: 120,
      diastolic: 80,
      measured_at: "2025-06-15T12:00:00Z",
    };
    expect(log.systolic).toBe(120);
    expect(log.pulse).toBeUndefined();
  });

  it("DashboardData can be empty", () => {
    const dashboard: DashboardData = {
      weight_trend: [],
      bp_trend: [],
    };
    expect(dashboard.latest_bp).toBeUndefined();
    expect(dashboard.weight_trend).toEqual([]);
  });

  it("MealPlan has entries array", () => {
    const plan: MealPlan = {
      id: "1",
      week_start_date: "2025-06-16",
      entries: [
        {
          id: "e1",
          day_of_week: 0,
          meal_type: "breakfast",
          custom_meal_json: { name: "Oatmeal" },
        },
      ],
    };
    expect(plan.entries).toHaveLength(1);
  });

  it("ShoppingList with items", () => {
    const list: ShoppingList = {
      id: "1",
      name: "Weekly",
      status: "active",
      items: [
        {
          id: "i1",
          name: "Milk",
          is_checked: false,
          is_ai_suggested: false,
        },
      ],
    };
    expect(list.items[0].is_checked).toBe(false);
  });
});
