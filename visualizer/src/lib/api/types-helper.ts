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

export type Task = components['schemas']['TaskResponse'];
export type ImportResponse = components['schemas']['ImportResponse'];
export type BacktestResponse = components['schemas']['BacktestResponse'];
export type ConfigUpdateResponse = components['schemas']['ConfigUpdateResponse'];
export type ExchangeApiKeyResponse = components['schemas']['ExchangeApiKeyResponse'];
export type MessageResponse = components['schemas']['MessageResponse'];
export type StatusResponse = components['schemas']['StatusResponse'];
export type StrategiesResponse = components['schemas']['StrategiesResponse'];
export type SupportedSymbolsResponse = components['schemas']['SupportedSymbolsResponse'];
export type SupportedExchangesResponse = components['schemas']['SupportedExchangesResponse'];
export type TradeTokenResponse = components['schemas']['TradeTokenResponse'];
