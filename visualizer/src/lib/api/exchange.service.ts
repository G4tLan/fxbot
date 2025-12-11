import { api } from './client';
import type {
  DeleteExchangeApiKeyRequest,
  ExchangeSupportedSymbolsRequest,
  StoreExchangeApiKeyRequest,
} from './types-helper';

export interface ExchangeApiKey {
  id: number;
  exchange_name: string;
  name: string;
  api_key: string;
}

export const exchangeService = {
  getApiKeys: async () => {
    return api.get<ExchangeApiKey[]>('/api/v1/exchange/api-keys');
  },

  storeApiKey: async (data: StoreExchangeApiKeyRequest) => {
    return api.post<void>('/api/v1/exchange/api-keys/store', data);
  },

  deleteApiKey: async (data: DeleteExchangeApiKeyRequest) => {
    return api.post<void>('/api/v1/exchange/api-keys/delete', data);
  },

  getSupportedSymbols: async (exchangeName: string) => {
    const payload: ExchangeSupportedSymbolsRequest = { exchange_name: exchangeName };
    return api.post<string[]>('/api/v1/exchange/supported-symbols', payload);
  },
};
