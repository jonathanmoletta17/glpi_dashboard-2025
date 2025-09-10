import 'vitest/globals';
import type { TestingLibraryMatchers } from '@testing-library/jest-dom/matchers';

// Playwright-like matchers for E2E tests
interface PlaywrightMatchers<T = unknown> {
  toBeVisible(): T;
  toContainText(text: string): T;
  toHaveText(text: string): T;
  toHaveValue(value: string): T;
  toBeEnabled(): T;
  toBeDisabled(): T;
  toBeChecked(): T;
  toHaveAttribute(name: string, value?: string): T;
  toHaveClass(className: string): T;
}

declare module 'vitest' {
  interface Assertion<T = unknown>
    extends TestingLibraryMatchers<T, void>,
      PlaywrightMatchers<T> {
    toHaveNoViolations(): T;
  }
  interface AsymmetricMatchersContaining
    extends TestingLibraryMatchers<unknown, void>,
      PlaywrightMatchers<unknown> {
    toHaveNoViolations(): unknown;
  }
}
