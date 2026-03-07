import { test, expect } from '@playwright/test';

const TOTAL_TRAILS = 119;

test.describe('Trail Selection', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('page loads with title and header', async ({ page }) => {
    await expect(page.locator('text=Killington Trail Tracker')).toBeVisible();
    await expect(page.locator('text=My Ski Runs')).toBeVisible();
  });

  test('displays all peaks in the trail list', async ({ page }) => {
    const peakNames = [
      'Snowshed',
      'Sunrise',
      'Ramshead',
      'Snowdon',
      'Skye Peak',
      'Killington Peak',
      'Bear Mountain',
    ];
    for (const name of peakNames) {
      await expect(page.locator(`text=${name}`).first()).toBeVisible();
    }
  });

  test('stats panel shows 0 skied initially', async ({ page }) => {
    await expect(page.locator('text=Your Progress')).toBeVisible();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (0%)`)).toBeVisible();
  });

  test('clicking a trail in the list marks it as skied', async ({ page }) => {
    const trailRow = page.locator('text=Yodeler').first();
    await expect(trailRow).toBeVisible();
    await trailRow.click();

    // Should show checkmark
    await expect(page.locator('text=✓').first()).toBeVisible();

    // Stats should update to 1
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();
  });

  test('clicking a skied trail unmarks it', async ({ page }) => {
    const trailRow = page.locator('text=Yodeler').first();
    await trailRow.click();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();

    // Click again to unmark
    await trailRow.click();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (0%)`)).toBeVisible();
  });

  test('skied trails persist across page reload', async ({ page }) => {
    const trailRow = page.locator('text=Yodeler').first();
    await trailRow.click();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();

    await page.reload();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();
  });

  test('reset button clears all skied trails', async ({ page }) => {
    await page.locator('text=Yodeler').first().click();
    await page.locator('text=Idler').first().click();
    // 2 out of 119 = 2%
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (2%)`)).toBeVisible();

    await page.locator('button:has-text("Reset")').click();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (0%)`)).toBeVisible();
  });

  test('multiple trails can be selected', async ({ page }) => {
    const trailNames = ['Yodeler', 'Idler', 'Snow Play'];
    for (const name of trailNames) {
      await page.locator(`text=${name}`).first().click();
    }
    // 3 out of 119 = 3%
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (3%)`)).toBeVisible();
  });
});

test.describe('Difficulty Filters', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('all difficulty filters are active by default', async ({ page }) => {
    await expect(page.locator('button:has-text("Easy")')).toBeVisible();
    await expect(page.locator('button:has-text("Intermediate")')).toBeVisible();
    await expect(page.locator('button:has-text("Advanced")')).toBeVisible();
    await expect(page.locator('button:has-text("Expert")')).toBeVisible();
  });

  test('toggling difficulty filter hides trails of that difficulty', async ({ page }) => {
    await expect(page.locator('text=Outer Limits').first()).toBeVisible();

    await page.locator('button:has-text("Expert")').click();

    await expect(page.locator('text=Outer Limits')).toBeHidden();
  });

  test('toggling difficulty filter back shows trails again', async ({ page }) => {
    await page.locator('button:has-text("Expert")').click();
    await expect(page.locator('text=Outer Limits')).toBeHidden();

    await page.locator('button:has-text("Expert")').click();
    await expect(page.locator('text=Outer Limits').first()).toBeVisible();
  });

  test('filter mode buttons work (All / Skied / Not Skied)', async ({ page }) => {
    // Mark a trail as skied first
    await page.locator('text=Yodeler').first().click();

    // Switch to "Skied" mode - use exact match to avoid matching "Not Skied"
    await page.getByRole('button', { name: 'Skied', exact: true }).click();

    // Should only show skied trails
    await expect(page.locator('text=Yodeler').first()).toBeVisible();
    await expect(page.locator('text=Idler')).toBeHidden();

    // Switch to "Not Skied" mode
    await page.getByRole('button', { name: 'Not Skied' }).click();

    await expect(page.locator('text=Yodeler')).toBeHidden();
    await expect(page.locator('text=Idler').first()).toBeVisible();

    // Switch back to "All"
    await page.getByRole('button', { name: 'All' }).click();
    await expect(page.locator('text=Yodeler').first()).toBeVisible();
    await expect(page.locator('text=Idler').first()).toBeVisible();
  });
});

test.describe('Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('search input filters trails by name', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search trails..."]');
    await searchInput.fill('Superstar');

    await expect(page.locator('text=Superstar').first()).toBeVisible();
    await expect(page.locator('text=Yodeler')).toBeHidden();
  });

  test('search shows empty state when no matches', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search trails..."]');
    await searchInput.fill('xyznonexistent');

    await expect(page.locator('text=No trails match your filters')).toBeVisible();
  });

  test('clearing search shows all trails again', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search trails..."]');
    await searchInput.fill('Superstar');
    await expect(page.locator('text=Yodeler')).toBeHidden();

    await searchInput.clear();
    await expect(page.locator('text=Yodeler').first()).toBeVisible();
  });
});
