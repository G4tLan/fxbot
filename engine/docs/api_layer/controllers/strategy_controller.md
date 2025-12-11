# Strategy Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Strategy Controller handles the management of strategy files. It allows users to create new strategies, list existing ones, and save changes to strategy code.

## Key Endpoints

### `POST /strategy/make`
Generates a new strategy file from a template.
- **Input**: `NewStrategyRequestJson` (name)
- **Requires Auth**: Yes

### `GET /strategy/all`
Lists all available strategies in the project.
- **Requires Auth**: Yes

### `POST /strategy/get`
Retrieves the code content of a specific strategy.
- **Input**: `GetStrategyRequestJson`
- **Requires Auth**: Yes
