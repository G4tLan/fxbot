# Auth Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Auth Controller handles user authentication and session management. It provides endpoints for logging in, managing the application lifecycle (shutdown/terminate), and handling engine Trade tokens.

## Key Endpoints

### `POST /auth/login`
Authenticates the user with a password and returns a JWT token.
- **Input**: `LoginRequestJson` (password)
- **Output**: JWT Token

### `POST /auth/terminate-all`
Terminates all running background processes (backtests, optimizations, etc.).
- **Requires Auth**: Yes

### `POST /auth/shutdown`
Gracefully shuts down the entire engine application.
- **Requires Auth**: Yes

### `POST /auth/engine-trade-token`
Exchanges the local license token for a engine Trade bearer token, enabling interaction with the engine Trade platform.
- **Requires Auth**: Yes
