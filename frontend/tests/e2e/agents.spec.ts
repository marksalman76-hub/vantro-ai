import { test, expect } from '@playwright/test';

const E2E_EMAIL = process.env.E2E_EMAIL || 'test@example.com';
const E2E_PASSWORD = process.env.E2E_PASSWORD || 'testpassword';

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.fill('input[type="email"]', E2E_EMAIL);
  await page.fill('input[type="password"]', E2E_PASSWORD);
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
}

test('should list available agents', async ({ page }) => {
  await login(page);
  await page.goto('/dashboard/agents');
  // At least one agent card should be visible
  const agentCards = page.locator('[data-testid="agent-card"], .agent-card, .bg-gray-900.border.border-gray-800.rounded-2xl').first();
  await expect(agentCards).toBeVisible({ timeout: 10000 });
});

test('should open run agent modal', async ({ page }) => {
  await login(page);
  await page.goto('/dashboard/agents');
  // Click the first "Run" button on an agent card
  const runButton = page.getByRole('button', { name: /run/i }).first();
  await expect(runButton).toBeVisible({ timeout: 10000 });
  await runButton.click();
  // Modal or drawer should open — look for a modal container or dialog
  const modal = page.locator('[role="dialog"], [data-testid="run-modal"], .modal, .drawer').first();
  await expect(modal).toBeVisible({ timeout: 5000 });
});
