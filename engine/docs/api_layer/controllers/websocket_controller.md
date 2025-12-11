# Websocket Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Websocket Controller manages the real-time communication channel between the backend and the dashboard. It streams logs, chart data, and progress updates.

## Key Endpoints

### `WS /ws`
The main WebSocket endpoint.
- **Query Param**: `token` (for authentication)
- **Behavior**: Subscribes to Redis channels and forwards messages to the connected client.
