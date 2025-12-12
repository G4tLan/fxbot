import { backtestService } from '$lib/api/backtest.service';
import type {
  BacktestRequest,
  BacktestResponse,
  BacktestSessionResponse,
  PaginationRequest,
} from '$lib/api/types-helper';
import { writable } from 'svelte/store';
import { taskStore } from './task.store';
import { toastStore } from './toast.store';

interface BacktestState {
  loading: boolean;
  lastResult: BacktestResponse | null;
  sessions: BacktestSessionResponse[];
  totalSessions: number;
}

const initialState: BacktestState = {
  loading: false,
  lastResult: null,
  sessions: [],
  totalSessions: 0,
};

function createBacktestStore() {
  const { subscribe, update, set } = writable<BacktestState>(initialState);

  return {
    subscribe,

    runBacktest: async (data: BacktestRequest) => {
      update((s) => ({ ...s, loading: true, lastResult: null }));
      try {
        const response = await backtestService.triggerBacktest(data);

        if (data.run_in_background && response.task_id) {
          // If running in background, add to task store
          taskStore.addBacktestTask(response);
          toastStore.success('Backtest started in background');
        } else {
          // If synchronous, show success
          toastStore.success('Backtest completed');
          update((s) => ({ ...s, lastResult: response }));
        }

        update((s) => ({ ...s, loading: false }));
        return response;
      } catch (error) {
        console.error('Backtest failed', error);
        toastStore.error('Backtest failed to start');
        update((s) => ({ ...s, loading: false }));
        throw error;
      }
    },

    loadSessions: async (params: PaginationRequest = { page: 1, limit: 10, offset: 0 }) => {
      update((s) => ({ ...s, loading: true }));
      try {
        const response = await backtestService.getSessions(params);
        update((s) => ({
          ...s,
          sessions: response.sessions,
          totalSessions: response.count,
          loading: false,
        }));
      } catch (error) {
        console.error('Failed to load sessions', error);
        toastStore.error('Failed to load backtest sessions');
        update((s) => ({ ...s, loading: false }));
      }
    },

    deleteSession: async (sessionId: string) => {
      try {
        await backtestService.deleteSession(sessionId);
        update((s) => ({
          ...s,
          sessions: s.sessions.filter((session) => session.id !== sessionId),
          totalSessions: s.totalSessions - 1,
        }));
        toastStore.success('Session deleted');
      } catch (error) {
        console.error('Failed to delete session', error);
        toastStore.error('Failed to delete session');
      }
    },

    reset: () => set(initialState),
  };
}

export const backtestStore = createBacktestStore();
