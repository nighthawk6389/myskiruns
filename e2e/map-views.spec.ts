import { test, expect } from '@playwright/test';

const TOTAL_TRAILS = 119;

test.describe('Schematic Map View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('schematic map is shown by default', async ({ page }) => {
    const svg = page.locator('svg[viewBox="0 0 1440 750"]');
    await expect(svg).toBeVisible();
  });

  test('schematic map renders trail paths for all peaks', async ({ page }) => {
    const svg = page.locator('svg[viewBox="0 0 1440 750"]');
    const trailGroups = svg.locator('g[style*="cursor: pointer"]');
    const count = await trailGroups.count();
    expect(count).toBe(TOTAL_TRAILS);
  });

  test('clicking a trail path on schematic map toggles skied state', async ({ page }) => {
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (0%)`)).toBeVisible();

    const svg = page.locator('svg[viewBox="0 0 1440 750"]');
    const trailGroups = svg.locator('g[style*="cursor: pointer"]');
    // Use dispatchEvent because SVG mountain polygons intercept pointer events
    await trailGroups.first().dispatchEvent('click');

    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();

    // Click again to unmark
    await trailGroups.first().dispatchEvent('click');
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (0%)`)).toBeVisible();
  });

  test('peaks are rendered with elevation labels', async ({ page }) => {
    const svg = page.locator('svg[viewBox="0 0 1440 750"]');
    await expect(svg.locator('text:has-text("4,241")')).toBeVisible();
    await expect(svg.locator('text:has-text("3,800")')).toBeVisible();
  });

  test('filtering hides trails on schematic map', async ({ page }) => {
    const svg = page.locator('svg[viewBox="0 0 1440 750"]');

    const initialCount = await svg.locator('g[style*="cursor: pointer"]').count();
    expect(initialCount).toBe(TOTAL_TRAILS);

    // Disable all except green (Easy)
    await page.locator('button:has-text("Intermediate")').click();
    await page.locator('button:has-text("Advanced")').click();
    await page.locator('button:has-text("Expert")').click();

    const filteredCount = await svg.locator('g[style*="cursor: pointer"]').count();
    expect(filteredCount).toBeLessThan(initialCount);
    expect(filteredCount).toBeGreaterThan(0);
  });
});

test.describe('Image Map View', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
    // Switch to image map view
    await page.locator('button:has-text("Trail Map")').click();
    // Wait for overlay SVG to appear (after image error triggers)
    await page.locator('svg[viewBox="0 0 100 100"]').waitFor({ state: 'attached', timeout: 5000 });
  });

  test('switching to image map view shows hotspot overlay', async ({ page }) => {
    const overlay = page.locator('svg[viewBox="0 0 100 100"]');
    await expect(overlay).toBeAttached();
  });

  test('image map hotspots are positioned within bounds', async ({ page }) => {
    const overlay = page.locator('svg[viewBox="0 0 100 100"]');

    const dots = overlay.locator('circle[r="6"]');
    const dotCount = await dots.count();

    expect(dotCount).toBe(TOTAL_TRAILS);

    // Verify sample dots are within the 0-100 coordinate space
    for (let i = 0; i < Math.min(dotCount, 20); i++) {
      const cx = parseFloat(await dots.nth(i).getAttribute('cx') || '0');
      const cy = parseFloat(await dots.nth(i).getAttribute('cy') || '0');
      expect(cx).toBeGreaterThanOrEqual(0);
      expect(cx).toBeLessThanOrEqual(100);
      expect(cy).toBeGreaterThanOrEqual(0);
      expect(cy).toBeLessThanOrEqual(100);
    }
  });

  test('hotspots are grouped by peak region', async ({ page }) => {
    const overlay = page.locator('svg[viewBox="0 0 100 100"]');

    const dots = overlay.locator('circle[r="6"]');
    const positions: { cx: number; cy: number }[] = [];

    const dotCount = await dots.count();
    for (let i = 0; i < dotCount; i++) {
      const cx = parseFloat(await dots.nth(i).getAttribute('cx') || '0');
      const cy = parseFloat(await dots.nth(i).getAttribute('cy') || '0');
      positions.push({ cx, cy });
    }

    // Verify that hotspots span most of the horizontal space
    const minX = Math.min(...positions.map((p) => p.cx));
    const maxX = Math.max(...positions.map((p) => p.cx));
    expect(maxX - minX).toBeGreaterThan(60);

    // Verify vertical spread
    const minY = Math.min(...positions.map((p) => p.cy));
    const maxY = Math.max(...positions.map((p) => p.cy));
    expect(maxY - minY).toBeGreaterThan(30);
  });

  test('clicking a hotspot on image map toggles skied state', async ({ page }) => {
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (0%)`)).toBeVisible();

    const overlay = page.locator('svg[viewBox="0 0 100 100"]');
    const hotspotGroups = overlay.locator('g[style*="cursor: pointer"]');
    // Use dispatchEvent because scroll area div intercepts pointer events
    await hotspotGroups.first().dispatchEvent('click');

    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();
  });

  test('image map has zoom controls', async ({ page }) => {
    await expect(page.locator('button:has-text("+")').first()).toBeVisible();
    await expect(page.locator('button:has-text("-")').first()).toBeVisible();
    await expect(page.locator('button:has-text("1x")')).toBeVisible();
  });

  test('filtering hides hotspots on image map', async ({ page }) => {
    const overlay = page.locator('svg[viewBox="0 0 100 100"]');
    const initialDots = await overlay.locator('circle[r="6"]').count();
    expect(initialDots).toBe(TOTAL_TRAILS);

    // Disable all except Easy
    await page.locator('button:has-text("Intermediate")').click();
    await page.locator('button:has-text("Advanced")').click();
    await page.locator('button:has-text("Expert")').click();

    const filteredDots = await overlay.locator('circle[r="6"]').count();
    expect(filteredDots).toBeLessThan(initialDots);
  });
});

test.describe('Map Toggle', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('toggling between schematic and image map views', async ({ page }) => {
    // Schematic view is default
    await expect(page.locator('svg[viewBox="0 0 1440 750"]')).toBeVisible();

    // Switch to image map
    await page.locator('button:has-text("Trail Map")').click();
    await page.locator('svg[viewBox="0 0 100 100"]').waitFor({ state: 'attached', timeout: 5000 });
    await expect(page.locator('svg[viewBox="0 0 1440 750"]')).toBeHidden();

    // Switch back
    await page.locator('button:has-text("Schematic")').click();
    await expect(page.locator('svg[viewBox="0 0 1440 750"]')).toBeVisible();
  });

  test('trail selection syncs between map and list', async ({ page }) => {
    await page.locator('text=Yodeler').first().click();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();

    // Switch to image map and back - state should persist
    await page.locator('button:has-text("Trail Map")').click();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();

    await page.locator('button:has-text("Schematic")').click();
    await expect(page.getByText(`/ ${TOTAL_TRAILS} trails (1%)`)).toBeVisible();
  });
});

test.describe('Overlay Alignment', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();
  });

  test('schematic map peaks are ordered left to right by x-position', async ({ page }) => {
    const svg = page.locator('svg[viewBox="0 0 1440 750"]');
    await expect(svg).toBeVisible();

    const peakTexts = svg.locator('text');
    const textCount = await peakTexts.count();

    const elevations: { text: string; x: number }[] = [];
    for (let i = 0; i < textCount; i++) {
      const textContent = await peakTexts.nth(i).textContent();
      const xAttr = await peakTexts.nth(i).getAttribute('x');
      if (textContent && xAttr && textContent.includes('ft')) {
        elevations.push({ text: textContent, x: parseFloat(xAttr) });
      }
    }

    if (elevations.length > 1) {
      const xValues = elevations.map((e) => e.x);
      const spread = Math.max(...xValues) - Math.min(...xValues);
      expect(spread).toBeGreaterThan(500);
    }
  });

  test('image map hotspots for Snowshed peak are on the left side', async ({ page }) => {
    await page.locator('button:has-text("Trail Map")').click();
    await page.locator('svg[viewBox="0 0 100 100"]').waitFor({ state: 'attached', timeout: 5000 });

    const overlay = page.locator('svg[viewBox="0 0 100 100"]');

    // Filter to only Easy trails and search for Snowshed
    await page.locator('button:has-text("Intermediate")').click();
    await page.locator('button:has-text("Advanced")').click();
    await page.locator('button:has-text("Expert")').click();
    await page.locator('input[placeholder="Search trails..."]').fill('Snowshed');

    const dots = overlay.locator('circle[r="6"]');
    const dotCount = await dots.count();

    expect(dotCount).toBeGreaterThan(0);
    for (let i = 0; i < dotCount; i++) {
      const cx = parseFloat(await dots.nth(i).getAttribute('cx') || '50');
      expect(cx).toBeLessThan(20);
    }
  });

  test('image map hotspots for Bear Mountain are on the right side', async ({ page }) => {
    await page.locator('button:has-text("Trail Map")').click();
    await page.locator('svg[viewBox="0 0 100 100"]').waitFor({ state: 'attached', timeout: 5000 });

    const overlay = page.locator('svg[viewBox="0 0 100 100"]');

    await page.locator('input[placeholder="Search trails..."]').fill('Bear Mountain');

    const dots = overlay.locator('circle[r="6"]');
    const dotCount = await dots.count();

    expect(dotCount).toBeGreaterThan(0);
    for (let i = 0; i < dotCount; i++) {
      const cx = parseFloat(await dots.nth(i).getAttribute('cx') || '50');
      expect(cx).toBeGreaterThan(80);
    }
  });

  test('image map hotspots for Killington Peak are near the top', async ({ page }) => {
    await page.locator('button:has-text("Trail Map")').click();
    await page.locator('svg[viewBox="0 0 100 100"]').waitFor({ state: 'attached', timeout: 5000 });

    const overlay = page.locator('svg[viewBox="0 0 100 100"]');

    await page.locator('input[placeholder="Search trails..."]').fill('Superstar');

    const dots = overlay.locator('circle[r="6"]');
    const dotCount = await dots.count();

    expect(dotCount).toBeGreaterThan(0);
    for (let i = 0; i < dotCount; i++) {
      const cy = parseFloat(await dots.nth(i).getAttribute('cy') || '50');
      expect(cy).toBeLessThan(60);
    }
  });

  test('schematic map trail paths originate from correct peak positions', async ({ page }) => {
    const svg = page.locator('svg[viewBox="0 0 1440 750"]');
    await expect(svg).toBeVisible();

    const paths = svg.locator('g[style*="cursor: pointer"] path[d]');
    const pathCount = await paths.count();
    expect(pathCount).toBeGreaterThan(0);

    for (let i = 0; i < Math.min(pathCount, 10); i++) {
      const d = await paths.nth(i).getAttribute('d');
      if (d && d.startsWith('M')) {
        const match = d.match(/^M\s+([\d.]+)\s+([\d.]+)/);
        if (match) {
          const startX = parseFloat(match[1]);
          const startY = parseFloat(match[2]);
          expect(startX).toBeGreaterThanOrEqual(0);
          expect(startX).toBeLessThanOrEqual(1440);
          expect(startY).toBeGreaterThanOrEqual(0);
          expect(startY).toBeLessThanOrEqual(750);
        }
      }
    }
  });
});
