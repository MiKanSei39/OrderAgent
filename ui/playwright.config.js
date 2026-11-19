import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests', testMatch: 'browser.spec.js', workers: 1,
  use: { baseURL: 'http://127.0.0.1:18001', browserName: 'chromium', channel: 'msedge', headless: true, viewport: { width: 1440, height: 1050 } },
  webServer: { command: '"..\\.venv\\Scripts\\python.exe" "..\\scripts\\ui_test_server.py"', url: 'http://127.0.0.1:18001/health', reuseExistingServer: false, timeout: 120000 },
})
