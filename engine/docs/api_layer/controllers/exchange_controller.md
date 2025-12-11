# Exchange Controller

[← Back to API Layer Overview](../overview.md)

## Purpose
The Exchange Controller manages exchange-related data, such as API keys and supported symbols.

## Key Endpoints

### `POST /exchange/supported-symbols`
Returns a list of supported symbols for a given exchange.
- **Input**: `ExchangeSupportedSymbolsRequestJson`
- **Requires Auth**: Yes

### `GET /exchange/api-keys`
Retrieves the stored API keys for configured exchanges.
- **Requires Auth**: Yes

### `POST /exchange/api-keys/store`
Stores a new API key for an exchange.
- **Input**: `StoreExchangeApiKeyRequestJson`
- **Requires Auth**: Yes

### `POST /exchange/api-keys/delete`
Deletes a stored API key.
- **Input**: `DeleteExchangeApiKeyRequestJson`
- **Requires Auth**: Yes
