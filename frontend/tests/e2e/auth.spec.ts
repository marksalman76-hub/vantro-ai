import { test, expect } from "@playwright/test";

const BASE = process.env.BASE_URL || "http://localhost:3000";

test.describe("Authentication flow", () => {
  test("home page loads and shows hero content", async ({ page }) => {
    await page.goto(BASE);
    await expect(page).toHaveTitle(/Vantro/i);
    await expect(page.locator("h1").first()).toBeVisible();
  });

  test("login page renders form", async ({ page }) => {
    await page.goto(`${BASE}/login`);
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test("login page shows error on wrong credentials", async ({ page }) => {
    await page.goto(`${BASE}/login`);
    await page.fill('input[type="email"]', "nobody@example.com");
    await page.fill('input[type="password"]', "wrongpassword");
    await page.click('button[type="submit"]');
    // Expect an error message to appear
    await expect(page.locator("text=/failed|invalid|error/i").first()).toBeVisible({ timeout: 5000 });
  });

  test("signup page renders form", async ({ page }) => {
    await page.goto(`${BASE}/signup`);
    await expect(page).toHaveTitle(/trial|sign|vantro/i);
    await expect(page.locator("h1").first()).toBeVisible();
  });

  test("nav links are present on home page", async ({ page }) => {
    await page.goto(BASE);
    // Navbar should be rendered
    await expect(page.locator("nav")).toBeVisible();
  });
});
