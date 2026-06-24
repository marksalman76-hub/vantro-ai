import { test, expect } from "@playwright/test";

const BASE = process.env.BASE_URL || "http://localhost:3000";

test.describe("Billing / Pricing flow", () => {
  test("pricing page loads and shows plan cards", async ({ page }) => {
    await page.goto(`${BASE}/pricing`);
    await expect(page.locator("h1, h2").first()).toBeVisible();
    // At least one plan should be visible
    const cards = page.locator("[data-testid='plan-card'], .plan-card, article");
    await expect(cards.first()).toBeVisible({ timeout: 8000 });
  });

  test("pricing page has upgrade / get started buttons", async ({ page }) => {
    await page.goto(`${BASE}/pricing`);
    const btn = page.locator("a, button").filter({ hasText: /get started|choose|upgrade|select/i }).first();
    await expect(btn).toBeVisible({ timeout: 8000 });
  });

  test("unauthenticated billing redirect goes to login", async ({ page }) => {
    // Mock the auth check so we can test the redirect
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({ status: 401, body: JSON.stringify({ detail: "Not authenticated" }) })
    );
    await page.goto(`${BASE}/dashboard/billing`);
    // Should redirect to login when unauthenticated
    await page.waitForURL(/\/(login|signin)/i, { timeout: 8000 });
    await expect(page).toHaveURL(/\/(login|signin)/i);
  });

  test("clicking upgrade on pricing redirects to checkout or login", async ({ page }) => {
    await page.goto(`${BASE}/pricing`);
    const btn = page.locator("a, button").filter({ hasText: /get started|choose|upgrade|select/i }).first();
    await btn.click();
    // Should go to login (unauthenticated) or stripe checkout
    await page.waitForURL(/login|signin|checkout\.stripe\.com|dashboard/i, { timeout: 8000 });
    const url = page.url();
    expect(url).toMatch(/login|signin|checkout\.stripe\.com|dashboard/i);
  });
});
