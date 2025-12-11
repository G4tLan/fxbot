import { api } from './client';
import type {
  DeleteExchangeApiKeyRequest,
  ExchangeApiKeyResponse,
  ExchangeSupportedSymbolsRequest,
  StatusResponse,
  StoreExchangeApiKeyRequest,
  SupportedSymbolsResponse,
} from './types-helper';

export const exchangeService = {
  getApiKeys: async () => {
    return api.get<ExchangeApiKeyResponse[]>('/api/v1/exchange/api-keys');
  },

  storeApiKey: async (data: StoreExchangeApiKeyRequest) => {
    return api.post<StatusResponse>('/api/v1/exchange/api-keys/store', data);
  },

  deleteApiKey: async (data: DeleteExchangeApiKeyRequest) => {
    return api.post<StatusResponse>('/api/v1/exchange/api-keys/delete', data);
  },

  getSupportedSymbols: async (exchangeName: string) => {
    const payload: ExchangeSupportedSymbolsRequest = { exchange_name: exchangeName };
    return api.post<SupportedSymbolsResponse>('/api/v1/exchange/supported-symbols', payload);
  },
};
