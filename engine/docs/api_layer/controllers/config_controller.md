# Config Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Config Controller handles the reading and writing of the system configuration. It allows the dashboard to fetch the current settings and update them.

## Key Endpoints

### `POST /config/get`
Retrieves the current system configuration.
- **Input**: `ConfigRequestJson`
- **Output**: JSON object containing configuration settings.
- **Requires Auth**: Yes

### `POST /config/update`
Updates the system configuration with new values.
- **Input**: `ConfigRequestJson` (new config values)
- **Requires Auth**: Yes
