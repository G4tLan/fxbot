# Notification Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Notification Controller manages API keys and configurations for external notification services (e.g., Telegram, Discord).

## Key Endpoints

### `GET /notification/api-keys`
Retrieves all configured notification API keys.
- **Requires Auth**: Yes

### `POST /notification/api-keys/store`
Stores a new notification service configuration.
- **Input**: `StoreNotificationApiKeyRequestJson` (driver, fields)
- **Requires Auth**: Yes

### `POST /notification/api-keys/delete`
Deletes a notification configuration.
- **Input**: `DeleteNotificationApiKeyRequestJson`
- **Requires Auth**: Yes
