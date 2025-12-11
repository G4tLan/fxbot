# Implementation Plan

## Overview

This plan outlines the development phases to integrate the new Control Plane API (Port 8000) into the Visualizer. The goal is to enable user management, exchange configuration, and execution of backtests/imports directly from the UI.

## Architecture

- **API Layer:** `src/lib/api/` (Generated Schema + Services)
- **State Layer:** `src/lib/stores/` (Svelte Stores)
- **UI Layer:** `src/lib/components/` (Reusable Components) & `src/routes/` (Pages)

---

## UI/UX & Design Language

**Goal:** Create a professional, data-dense, and responsive interface suitable for trading operations.

### Design System (Tailwind CSS)

- **Theme:** Dark Mode First (Trading apps are typically dark).
  - **Backgrounds:** `bg-slate-900` (Main), `bg-slate-800` (Panels/Cards), `bg-slate-700` (Inputs/Hover).
  - **Text:** `text-slate-100` (Primary), `text-slate-400` (Secondary/Labels).
  - **Accents:**
    - **Primary Action:** `bg-blue-600` hover: `bg-blue-500`
    - **Success (Buy/Profit):** `text-green-400` / `bg-green-900/20`
    - **Danger (Sell/Loss):** `text-red-400` / `bg-red-900/20`
    - **Warning:** `text-yellow-400`

### Component Guidelines

1. **Layout:**
   - **Sidebar Navigation:** Collapsible sidebar for main modules (Dashboard, Backtest, Settings).
   - **Dashboard Grid:** specific layouts for high-density data (Charts + Tables).
2. **Data Display:**
   - **Tables:** Dense rows, sticky headers, sortable columns.
   - **Numbers:** Monospace font for prices/PnL (`font-mono`), aligned right.
   - **Status:** Color-coded badges (pills).
3. **Interactivity:**
   - **Feedback:** Loading spinners/skeletons for async operations.
   - **Toasts:** Notifications for success/error (e.g., "Import Started", "API Key Saved").
   - **Modals:** For critical actions (e.g., "Delete API Key") or complex forms.

---

## Phase 0: Foundations (Technical Setup)

**Goal:** Establish the core technical building blocks before building features.

### 1. Core Services

- [x] **HTTP Client:** Create a wrapper around `fetch` (or use `axios`) to handle:
  - Base URL configuration.
  - Global Error Handling (e.g., auto-logout on 401).
  - Request/Response Interceptors.
- [x] **Notification System:**
  - **Store:** `toast.store.ts` (add/remove toasts).
  - **Component:** `ToastContainer.svelte` & `Toast.svelte` (to display alerts).

### 2. Routing Security

- [x] **Route Guards:** Implement a client-side check (in `+layout.svelte` or hooks) to redirect unauthenticated users to `/login`.

---

## Phase 1: Authentication & Session Management

**Goal:** Allow users to register, login, and maintain a session. Secure the app.

### 1. Domain & API

- [x] **Types:** Export `LoginRequest`, `RegisterRequest`, `Token` in `types-helper.ts`.
- [x] **Service:** Create `src/lib/api/auth.service.ts`. (Implemented in `client.ts` and `auth.store.ts`)
  - Implement `login(credentials)`. **Note:** Must use `application/x-www-form-urlencoded` body (not JSON) to match backend `OAuth2PasswordRequestForm`.
  - Implement `register(data)`.
  - Implement `logout()`.
  - Helper to attach `Authorization: Bearer` header to requests.

### 2. State Management

- [x] **Store:** Create `src/lib/stores/auth.store.ts`.
  - Store `token` and `isAuthenticated` status.
  - Persist token in `localStorage`.

### 3. UI Components

- [x] **Components:**
  - `src/lib/components/auth/login-form.svelte` (Implemented in page)
  - `src/lib/components/auth/register-form.svelte` (Implemented in page)
- [x] **Pages:**
  - `src/routes/login/+page.svelte`
  - `src/routes/register/+page.svelte`
- [x] **Layout:** Update `src/routes/+layout.svelte` to show Login/Logout buttons based on state.

---

## Phase 2: Exchange API Key Management

**Goal:** Users can manage their exchange API keys securely.

### 1. Domain & API

- [x] **Types:** Export `StoreExchangeApiKeyRequest`, `DeleteExchangeApiKeyRequest` in `types-helper.ts`.
- [x] **Service:** Create `src/lib/api/exchange.service.ts`.
  - `getApiKeys()`
  - `storeApiKey(data)`
  - `deleteApiKey(id)` (Note: POST to `/exchange/api-keys/delete`)
  - `getSupportedSymbols(exchange)`

### 2. State Management

- [x] **Store:** Create `src/lib/stores/exchange.store.ts`.
  - `apiKeys`: List of stored keys.
  - `supportedSymbols`: Cache for symbols.

### 3. UI Components

- [x] **Components:**
  - `src/lib/components/exchange/api-key-list.svelte`
  - `src/lib/components/exchange/add-key-modal.svelte`
- [x] **Pages:**
  - `src/routes/settings/exchanges/+page.svelte`

---

## Phase 3: Data Import Workflow

**Goal:** Trigger background tasks to import candle data and track progress.

### 1. Domain & API

- [ ] **Types:** Export `ImportRequest`, `Task` in `types-helper.ts`.
- [ ] **Service:** Create `src/lib/api/import.service.ts` (or `task.service.ts`).
  - `triggerImport(data)` -> Returns `{ task_id, status }`.
  - `getTask(taskId)` -> Returns `Task` object with status (queued, processing, completed, failed) and result.

### 2. State Management

- [ ] **Store:** Create `src/lib/stores/import.store.ts` (or `task.store.ts`).
  - `activeTasks`: Map of `taskId` to `Task` status.
  - Action `pollTask(taskId)`: Periodically (10s) calls `getTask` until status is completed/failed.
  - Update UI with progress/completion.

### 3. UI Components

- [ ] **Components:**
  - `src/lib/components/import/import-form.svelte` (Select Exchange, Symbol, Date Range).
  - `src/lib/components/common/task-status.svelte` (Reusable component to show spinner/check/error for a task).
- [ ] **Pages:**
  - `src/routes/import/+page.svelte`

---

## Phase 4: Backtest Execution

**Goal:** Configure and trigger backtests (synchronous or asynchronous).

### 1. Domain & API

- [ ] **Types:** Export `BacktestRequest` in `types-helper.ts`.
- [ ] **Service:** Create `src/lib/api/backtest.service.ts`.
  - `triggerBacktest(data)` -> Returns results (sync) or `{ task_id }` (async).
  - Use `task.service.ts` for polling if running in background.

### 2. State Management

- [ ] **Store:** Create `src/lib/stores/backtest.store.ts`.
  - Form state for backtest configuration.

### 3. UI Components

- [ ] **Components:**
  - `src/lib/components/backtest/backtest-config-form.svelte`
- [ ] **Pages:**
  - `src/routes/backtest/new/+page.svelte`

---

## Phase 5: System Configuration

**Goal:** View and edit system-wide configurations.

### 1. Domain & API

- [ ] **Types:** Export `ConfigRequestJson`, `LspConfigResponse` in `types-helper.ts`.
- [ ] **Service:** Create `src/lib/api/config.service.ts`.
  - `getConfig()` (Note: POST to `/config/get`)
  - `updateConfig(updates)`
  - `getLspConfig()`

### 2. State Management

- [ ] **Store:** Create `src/lib/stores/config.store.ts`.
  - `systemConfig`: The current configuration object.

### 3. UI Components

- [ ] **Components:**
  - `src/lib/components/config/json-editor.svelte` (or form-based editor).
- [ ] **Pages:**
  - `src/routes/settings/system/+page.svelte`

---

## Phase 6: Strategy Editor (Advanced)

**Goal:** In-browser code editing for strategies using the LSP (Language Server Protocol).

### 1. Domain & API

- [ ] **Service:** `lsp.service.ts` to manage WebSocket connection to the backend LSP.

### 2. UI Components

- [ ] **Editor:** Integrate **Monaco Editor** (VS Code's editor).
- [ ] **Integration:** Connect Monaco to the WebSocket for autocomplete/linting (using `monaco-languageclient` or similar).
- [ ] **Page:** `src/routes/strategies/edit/+page.svelte`.

---

## Phase 7: Dashboard & System Operations

**Goal:** Provide a high-level overview and critical system controls (Panic Button).

### 1. Domain & API

- [ ] **Service:** Update `auth.service.ts` or create `system.service.ts`.
  - `shutdown()`
  - `terminateAll()` (Panic Button)
  - `generateEngineToken()`
- [ ] **WebSocket Service:** Create `src/lib/api/websocket.service.ts`.
  - Connect to `/ws` endpoint (Note: Pass token via query param `?token=...`).
  - Handle real-time events (status updates, trade notifications, backtest progress).

### 2. UI Components

- [ ] **Components:**
  - `src/lib/components/dashboard/stat-card.svelte` (Simple metric display).
  - `src/lib/components/system/panic-button.svelte` (Double-confirm modal for termination).
  - `src/lib/components/system/token-generator.svelte` (Display generated token).
- [ ] **Page:** `src/routes/+page.svelte` (The Dashboard).
  - Show system status.
  - Quick links to "New Backtest" or "Import".
  - Recent activity (if available).

---

## Phase 8: Quality Assurance & CI/CD

**Goal:** Ensure reliability and prevent regressions.

### 1. Testing Strategy

- [ ] **Unit Tests (`vitest`):**
  - Test `auth.store.ts` logic (login/logout state).
  - Test `api` services (mocking `fetch`).
- [ ] **E2E Tests (`playwright`):**
  - Test the "Happy Path": Login -> Configure Backtest -> Trigger.
  - Test Auth Guards (try to access protected route).

### 2. Deployment

- [ ] **Docker:** Create `Dockerfile` for the frontend (Nginx serving static build).
- [ ] **CI:** Setup GitHub Actions (or similar) to run `npm test` and `npm run build`.

---

## Phase 9: Live Trading Monitor (Future)

**Goal:** Real-time visualization of live trading execution.

### 1. Domain & API

- [ ] **Service:** Extend `websocket.service.ts` to handle live trading specific events (tick data, order fills).

### 2. UI Components

- [ ] **Page:** `src/routes/live/+page.svelte`.
  - Real-time Equity Curve.
  - Active Positions Table.
  - Live Log Stream.
