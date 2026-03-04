/**
 * 📸 Screenshot script for Aaron 2.0
 *
 * Takes screenshots of every page in the app for documentation.
 * Usage: npx playwright test scripts/take-screenshots.ts
 *    or: npx tsx scripts/take-screenshots.ts
 */

import { chromium } from "playwright";
import path from "path";
import fs from "fs";

const BASE_URL = process.env.BASE_URL || "http://localhost:3000";
const OUTPUT_DIR = path.resolve(__dirname, "../docs/screenshots");

const PAGES = [
  { name: "dashboard", path: "/", label: "Dashboard" },
  { name: "pantry", path: "/pantry", label: "Pantry" },
  { name: "recipes", path: "/recipes", label: "Recipes" },
  { name: "meal-planner", path: "/meal-planner", label: "Meal Planner" },
  { name: "food-log", path: "/food-log", label: "Food Log" },
  { name: "health", path: "/health", label: "Health Metrics" },
  { name: "coach", path: "/coach", label: "AI Coach" },
  { name: "settings", path: "/settings", label: "Settings" },
];

async function main() {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 2,
    colorScheme: "dark",
  });

  const page = await context.newPage();

  for (const { name, path: route, label } of PAGES) {
    const url = `${BASE_URL}${route}`;
    console.log(`📸 ${label} → ${url}`);

    await page.goto(url, { waitUntil: "networkidle" });

    // Wait for animations to settle
    await page.waitForTimeout(800);

    const filePath = path.join(OUTPUT_DIR, `${name}.png`);
    await page.screenshot({ path: filePath, fullPage: false });
    console.log(`   ✅ Saved ${filePath}`);
  }

  await browser.close();
  console.log(`\n🎉 Done! ${PAGES.length} screenshots saved to ${OUTPUT_DIR}`);
}

main().catch((err) => {
  console.error("❌ Screenshot failed:", err);
  process.exit(1);
});
