import { test, expect } from '@playwright/test';

const E2E_EMAIL = process.env.E2E_EMAIL || 'test@example.com';
const E2E_PASSWORD = process.env.E2E_PASSWORD || 'testpassword';

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.fill('input[type="email"]', E2E_EMAIL);
  await page.fill('input[type="password"]', E2E_PASSWORD);
  await page.click('button[type="submit"]');
  // Wait for redirect to dashboard
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
}

test('should load dashboard metrics', async ({ page }) => {
  await login(page);
  // 4 metric cards are present in the grid
  const metricCards = page.locator('.grid .bg-gray-900.border.border-gray-800.rounded-2xl');
  await expect(metricCards).toHaveCount(4, { timeout: 10000 });
});

test('should navigate to output library', async ({ page }) => {
  await login(page);
  // Click the Output Library link in the quick-actions grid or sidebar
  await page.click('a[href="/dashboard/library"]');
  await expect(page).toHaveURL(/\/library/);
});
