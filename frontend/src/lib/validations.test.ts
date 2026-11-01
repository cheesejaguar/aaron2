import { describe, it, expect } from "vitest";
import {
  bpLogSchema,
  cholesterolLogSchema,
  foodLogSchema,
  pantryItemSchema,
  settingsSchema,
  weightLogSchema,
} from "./validations";

function firstError(result: { success: boolean; error?: { issues: { message: string }[] } }) {
  return result.success ? undefined : result.error?.issues[0].message;
}

describe("pantryItemSchema", () => {
  it("defaults quantity to 1 and coerces numeric strings", () => {
    expect(pantryItemSchema.parse({ name: "Milk" }).quantity).toBe(1);
    expect(pantryItemSchema.parse({ name: "Milk", quantity: "2.5" }).quantity).toBe(2.5);
  });

  it("requires a name", () => {
    expect(firstError(pantryItemSchema.safeParse({ name: "" }))).toBe("Name is required");
  });

  it("rejects negative quantities", () => {
    expect(firstError(pantryItemSchema.safeParse({ name: "Milk", quantity: -1 }))).toBe(
      "Quantity must be positive",
    );
  });
});

describe("foodLogSchema", () => {
  it("accepts a valid meal and coerces nutrients", () => {
    const data = foodLogSchema.parse({ meal_type: "lunch", food_name: "Salad", calories: "300" });
    expect(data).toEqual({ meal_type: "lunch", food_name: "Salad", calories: 300 });
  });

  it("rejects unknown meal types", () => {
    expect(foodLogSchema.safeParse({ meal_type: "brunch", food_name: "Eggs" }).success).toBe(
      false,
    );
  });

  it("requires a food name", () => {
    expect(firstError(foodLogSchema.safeParse({ meal_type: "lunch", food_name: "" }))).toBe(
      "Food name is required",
    );
  });
});

describe("bpLogSchema", () => {
  it("accepts readings within range", () => {
    expect(bpLogSchema.parse({ systolic: "120", diastolic: "80" })).toEqual({
      systolic: 120,
      diastolic: 80,
    });
  });

  it.each([
    [{ systolic: 59, diastolic: 80 }, "Systolic must be at least 60"],
    [{ systolic: 301, diastolic: 80 }, "Systolic must be at most 300"],
    [{ systolic: 120, diastolic: 29 }, "Diastolic must be at least 30"],
    [{ systolic: 120, diastolic: 201 }, "Diastolic must be at most 200"],
  ])("rejects out-of-range reading %o", (input, message) => {
    expect(firstError(bpLogSchema.safeParse(input))).toBe(message);
  });

  it("bounds the optional pulse", () => {
    expect(bpLogSchema.safeParse({ systolic: 120, diastolic: 80, pulse: 251 }).success).toBe(
      false,
    );
  });
});

describe("weightLogSchema", () => {
  it.each([
    [49, "Weight must be at least 50 lbs"],
    [1001, "Weight must be at most 1000 lbs"],
  ])("rejects %d lbs", (weight, message) => {
    expect(firstError(weightLogSchema.safeParse({ weight_lbs: weight }))).toBe(message);
  });

  it("accepts boundary values", () => {
    expect(weightLogSchema.parse({ weight_lbs: 50 }).weight_lbs).toBe(50);
    expect(weightLogSchema.parse({ weight_lbs: "1000" }).weight_lbs).toBe(1000);
  });
});

describe("cholesterolLogSchema", () => {
  it("requires total within 50-500", () => {
    expect(cholesterolLogSchema.safeParse({ total_mg_dl: 49 }).success).toBe(false);
    expect(cholesterolLogSchema.safeParse({ total_mg_dl: 501 }).success).toBe(false);
    expect(cholesterolLogSchema.parse({ total_mg_dl: "200", ldl: "120" })).toEqual({
      total_mg_dl: 200,
      ldl: 120,
    });
  });
});

describe("settingsSchema", () => {
  it("requires a name", () => {
    expect(firstError(settingsSchema.safeParse({ name: "" }))).toBe("Name is required");
  });

  it("bounds the calorie target", () => {
    const parse = (calorie_target: number) =>
      settingsSchema.safeParse({ name: "Aaron", health_goals_json: { calorie_target } }).success;
    expect(parse(499)).toBe(false);
    expect(parse(2000)).toBe(true);
    expect(parse(10001)).toBe(false);
  });
});
