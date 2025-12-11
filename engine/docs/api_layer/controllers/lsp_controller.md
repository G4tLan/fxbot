# LSP Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The LSP (Language Server Protocol) Controller provides configuration for the editor integration, allowing features like auto-completion and syntax checking within the engine dashboard or connected IDEs.

## Key Endpoints

### `GET /lsp-config`
Returns the configuration for the Language Server, such as the WebSocket port and path.
- **Output**: JSON with `ws_port`, `ws_path`, etc.
- **Requires Auth**: Yes
