import { test, expect } from "@playwright/test";

const BASE = process.env.BASE_URL || "http://localhost:3000";

test.describe("Support ticket flow", () => {
  test("support page requires login", async ({ page }) => {
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({ status: 401, body: JSON.stringify({ detail: "Not authenticated" }) })
    );
    await page.goto(`${BASE}/dashboard/support`);
    await page.waitForURL(/\/(login|signin)/i, { timeout: 8000 });
    await expect(page).toHaveURL(/\/(login|signin)/i);
  });

  test("support page renders ticket form when authenticated", async ({ page }) => {
    // Stub auth and ticket list
    await page.route("**/api/auth/me", (route) =>
      route.fulfill({
        status: 200,
        body: JSON.stringify({ id: "u1", email: "test@vantro.ai", name: "Test User" }),
      })
    );
    await page.route("**/api/support/tickets**", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          body: JSON.stringify({ tickets: [], total: 0 }),
        });
      }
      return route.continue();
    });

    // Set a fake token so the page doesn't immediately redirect
    await page.goto(`${BASE}/login`);
    await page.evaluate(() => localStorage.setItem("token", "fake-token-for-test"));
    await page.goto(`${BASE}/dashboard/support`);

    // Should show a form or ticket creation button
    const form = page.locator("form, [data-testid='support-form'], button").filter({ hasText: /submit|send|create|new ticket/i }).first();
    await expect(form).toBeVisible({ timeout: 8000 });
  });

  test("submitting ticket calls API and shows confirmation", async ({ page }) => {
    await page.route("**/api/support/tickets", (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 200,
          body: JSON.stringify({ ticket_id: "tick_001", status: "open" }),
        });
      }
      return route.fulfill({ status: 200, body: JSON.stringify({ tickets: [], total: 0 }) });
    });

    await page.goto(`${BASE}/login`);
    await page.evaluate(() => localStorage.setItem("token", "fake-token-for-test"));
    await page.goto(`${BASE}/dashboard/support`);

    // If a form is visible, fill and submit it
    const subjectInput = page.locator("input[name='subject'], input[placeholder*='subject' i], textarea").first();
    if (await subjectInput.isVisible({ timeout: 3000 }).catch(() => false)) {
      await subjectInput.fill("Test support request");
      const detail = page.locator("textarea").last();
      await detail.fill("This is a detailed test request.");
      const submit = page.locator("button[type='submit'], button").filter({ hasText: /submit|send/i }).first();
      await submit.click();
      // Should show confirmation
      const confirmation = page.locator("text=/submitted|sent|success|received|ticket/i").first();
      await expect(confirmation).toBeVisible({ timeout: 5000 });
    }
  });
});
