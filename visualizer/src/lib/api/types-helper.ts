import type { components } from './schema';

export type BacktestRequest = components['schemas']['BacktestRequest'];
export type ConfigRequestJson = components['schemas']['ConfigRequestJson'];
export type ImportRequest = components['schemas']['ImportRequest'];
export type LspConfigResponse = components['schemas']['LspConfigResponse'];

// Auth
export type LoginRequest = components['schemas']['Body_login_api_v1_auth_login_post'];
export type RegisterRequest = components['schemas']['RegisterRequest'];
export type Token = components['schemas']['Token'];

// Exchange
export type StoreExchangeApiKeyRequest = components['schemas']['StoreExchangeApiKeyRequestJson'];
export type DeleteExchangeApiKeyRequest = components['schemas']['DeleteExchangeApiKeyRequestJson'];
export type ExchangeSupportedSymbolsRequest =
  components['schemas']['ExchangeSupportedSymbolsRequestJson'];

// Common Responses / Errors
export type HTTPValidationError = components['schemas']['HTTPValidationError'];
export type ValidationError = components['schemas']['ValidationError'];
