import { exchangeService } from '$lib/api/exchange.service';
import type { ExchangeApiKeyResponse, StoreExchangeApiKeyRequest } from '$lib/api/types-helper';
import { writable } from 'svelte/store';
import { toastStore } from './toast.store';

interface ExchangeState {
  apiKeys: ExchangeApiKeyResponse[];
  loading: boolean;
  supportedSymbols: Record<string, string[]>; // Cache by exchange name
  supportedExchanges: string[];
}

const initialState: ExchangeState = {
  apiKeys: [],
  loading: false,
  supportedSymbols: {},
  supportedExchanges: [],
};

function createExchangeStore() {
  const { subscribe, update, set } = writable<ExchangeState>(initialState);

  return {
    subscribe,

    loadSupportedExchanges: async () => {
      try {
        const response = await exchangeService.getSupportedExchanges();
        update((s) => ({ ...s, supportedExchanges: response.exchanges }));
      } catch (error) {
        console.error('Failed to load supported exchanges', error);
      }
    },

    loadApiKeys: async () => {
      update((s) => ({ ...s, loading: true }));
      try {
        const keys = await exchangeService.getApiKeys();
        update((s) => ({ ...s, apiKeys: keys, loading: false }));
      } catch (error) {
        console.error('Failed to load API keys', error);
        update((s) => ({ ...s, loading: false }));
      }
    },

    addApiKey: async (data: StoreExchangeApiKeyRequest) => {
      update((s) => ({ ...s, loading: true }));
      try {
        await exchangeService.storeApiKey(data);
        toastStore.success('API Key added successfully');
        // Reload keys to get the new ID
        const keys = await exchangeService.getApiKeys();
        update((s) => ({ ...s, apiKeys: keys, loading: false }));
        return true;
      } catch (error) {
        console.error('Failed to add API key', error);
        update((s) => ({ ...s, loading: false }));
        return false;
      }
    },

    deleteApiKey: async (id: number) => {
      update((s) => ({ ...s, loading: true }));
      try {
        await exchangeService.deleteApiKey({ id });
        toastStore.success('API Key deleted successfully');
        update((s) => ({
          ...s,
          apiKeys: s.apiKeys.filter((k) => k.id !== id),
          loading: false,
        }));
      } catch (error) {
        console.error('Failed to delete API key', error);
        update((s) => ({ ...s, loading: false }));
      }
    },

    loadSupportedSymbols: async (exchangeName: string) => {
      // Check cache first (optional, but good for performance)
      // For now, we'll just fetch fresh
      try {
        const response = await exchangeService.getSupportedSymbols(exchangeName);
        update((s) => ({
          ...s,
          supportedSymbols: {
            ...s.supportedSymbols,
            [exchangeName]: response.symbols,
          },
        }));
        return response.symbols;
      } catch (error) {
        console.error(`Failed to load symbols for ${exchangeName}`, error);
        return [];
      }
    },
  };
}

export const exchangeStore = createExchangeStore();
