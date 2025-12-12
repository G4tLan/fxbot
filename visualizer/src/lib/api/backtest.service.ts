import { api } from './client';
import type { BacktestRequest, BacktestResponse } from './types-helper';

export const backtestService = {
  triggerBacktest: async (data: BacktestRequest) => {
    return api.post<BacktestResponse>('/api/v1/backtest', data);
  },
};
