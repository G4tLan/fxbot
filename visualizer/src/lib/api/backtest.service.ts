import { api } from './client';
import type {
  BacktestRequest,
  BacktestResponse,
  BacktestSessionListResponse,
  BacktestSessionResponse,
  ChartDataResponse,
  LogsResponse,
  MessageResponse,
  PaginationRequest,
  PurgeResponse,
  StrategyCodeResponse,
  UpdateSessionNotesRequest,
  UpdateSessionStateRequest,
} from './types-helper';

export const backtestService = {
  triggerBacktest: async (data: BacktestRequest) => {
    return api.post<BacktestResponse>('/api/v1/backtest', data);
  },

  cancelBacktest: async (data: Record<string, string>) => {
    return api.post<MessageResponse>('/api/v1/cancel', data);
  },

  getSessions: async (data: PaginationRequest) => {
    return api.post<BacktestSessionListResponse>('/api/v1/sessions', data);
  },

  getSession: async (sessionId: string) => {
    return api.get<BacktestSessionResponse>(`/api/v1/sessions/${sessionId}`);
  },

  deleteSession: async (sessionId: string) => {
    return api.delete<MessageResponse>(`/api/v1/sessions/${sessionId}`);
  },

  getSessionLogs: async (sessionId: string) => {
    return api.get<LogsResponse>(`/api/v1/sessions/${sessionId}/logs`);
  },

  getSessionChartData: async (sessionId: string) => {
    return api.get<ChartDataResponse>(`/api/v1/sessions/${sessionId}/chart-data`);
  },

  updateSessionNotes: async (sessionId: string, data: UpdateSessionNotesRequest) => {
    return api.post<MessageResponse>(`/api/v1/sessions/${sessionId}/notes`, data);
  },

  updateSessionState: async (data: UpdateSessionStateRequest) => {
    return api.post<MessageResponse>('/api/v1/update-state', data);
  },

  getSessionStrategyCode: async (sessionId: string) => {
    return api.post<StrategyCodeResponse>(`/api/v1/sessions/${sessionId}/strategy-code`, {});
  },

  purgeSessions: async (data: Record<string, number>) => {
    return api.post<PurgeResponse>('/api/v1/purge-sessions', data);
  },
};
