import { api } from './client';
import type { StrategiesResponse } from './types-helper';

export const strategyService = {
  getStrategies: async () => {
    return api.get<StrategiesResponse>('/api/v1/strategies');
  },
};
