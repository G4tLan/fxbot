import { backtestService } from '$lib/api/backtest.service';
import type { BacktestRequest, BacktestResponse } from '$lib/api/types-helper';
import { writable } from 'svelte/store';
import { taskStore } from './task.store';
import { toastStore } from './toast.store';

interface BacktestState {
  loading: boolean;
  lastResult: BacktestResponse | null;
}

const initialState: BacktestState = {
  loading: false,
  lastResult: null,
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

    reset: () => set(initialState),
  };
}

export const backtestStore = createBacktestStore();
