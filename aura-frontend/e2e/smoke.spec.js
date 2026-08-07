import { test, expect } from '@playwright/test';

test.describe('Aura frontend smoke', () => {
  test('loads the home page and shows the brand', async ({ page }) => {
    await page.goto('/');
    // Brand text "Aura" appears in header
    await expect(page.getByRole('heading', { name: /Aura/ })).toBeVisible();
  });

  test('navigates to library and shows empty state', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /biblioteca/i }).click();
    await expect(page.getByRole('heading', { name: /Mi Biblioteca/i })).toBeVisible();
    // The empty state or the loaded list will be shown.
    await expect(page.locator('main')).toBeVisible();
  });

  test('navigates to favorites', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: /favoritos/i }).click();
    await expect(page.getByRole('heading', { name: /^Favoritos$/i })).toBeVisible();
  });

  test('settings modal opens and closes', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /abrir configuración/i }).click();
    await expect(page.getByRole('heading', { name: /Configuración de Aura/i })).toBeVisible();
    await page.getByRole('button', { name: /cerrar configuración/i }).click();
    await expect(page.getByRole('heading', { name: /Configuración de Aura/i })).not.toBeVisible();
  });

  test('search bar accepts input', async ({ page }) => {
    await page.goto('/');
    const input = page.getByPlaceholder(/busca por canción/i);
    await expect(input).toBeVisible();
    await input.fill('Daft Punk');
    await expect(input).toHaveValue('Daft Punk');
  });
});
