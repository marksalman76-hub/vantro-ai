import { test, expect } from "@playwright/test";

test("Billing page loads", async ({ page }) => {
  await page.goto("http://localhost:3000/client/billing");
  
  // Use the h1 heading instead (more specific)
  const heading = page.locator("h1:has-text('Billing and workspace credits')");
  await expect(heading).toBeVisible();
});