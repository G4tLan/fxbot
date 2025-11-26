import { selectedInterval, selectedRun, selectedTicker } from '$lib/stores';
import { derived, writable } from 'svelte/store';
import { tradeEngineService } from '../api/trade-engine.service';
import type { IndicatorEntry, IndicatorsResponse, TimeRange } from '../types';

// Indicators store with loading state and error handling
export interface IndicatorsStore {
  data: IndicatorsResponse | null;
  processedData?: Record<string, any>;
  loading: boolean;
  error: string | null;
}

/**
 * Creates an indicators store that automatically fetches indicator data
 * when ticker, interval, or run selection changes.
 */
function createIndicatorsStore() {
  const { subscribe, set, update } = writable<IndicatorsStore>({
    data: null,
    loading: false,
    error: null,
  });

  let currentFetchPromise: Promise<void> | null = null;
  let currentFetchId = 0;

  const fetchIndicators = async (
    ticker: string,
    interval: string,
    runName: string,
    indicatorKey?: string
  ) => {
    // Cancel any ongoing fetch
    currentFetchPromise = null;
    const fetchId = ++currentFetchId;

    update((state) => ({ ...state, loading: true, error: null }));

    const fetchPromise = (async () => {
      try {
        const indicators = await tradeEngineService.getIndicators(
          ticker,
          interval,
          runName,
          indicatorKey
        );

        // Only update if this is still the current fetch
        if (fetchId === currentFetchId) {
          set({
            data: indicators,
            processedData: { Consolidation: extractTimeRanges(indicators['Consolidation']) },
            loading: false,
            error: null,
          });
        }
      } catch (error) {
        // Only update if this is still the current fetch
        if (fetchId === currentFetchId) {
          console.error('Failed to fetch indicators:', error);
          set({
            data: null,
            loading: false,
            error: error instanceof Error ? error.message : 'Unknown error occurred',
          });
        }
      }
    })();

    // Set the current fetch promise after it's defined
    currentFetchPromise = fetchPromise;
    return fetchPromise;
  };

  const reset = () => {
    currentFetchPromise = null;
    currentFetchId = 0;
    set({
      data: null,
      loading: false,
      error: null,
    });
  };

  return {
    subscribe,
    fetchIndicators,
    reset,
  };
}

export const indicatorsStore = createIndicatorsStore();

export const indicators = derived(
  [selectedTicker, selectedInterval, selectedRun],
  ([$ticker, $interval, $run], set) => {
    // Reset state immediately
    set({
      data: null,
      loading: true,
      error: null,
    });

    if ($ticker && $interval && $run) {
      indicatorsStore.fetchIndicators($ticker, $interval, $run);
    }

    // Subscribe to indicatorsStore updates
    const unsubscribe = indicatorsStore.subscribe((value) => {
      set(value);
    });

    return unsubscribe;
  },
  {
    data: null,
    loading: false,
    error: null,
  } as IndicatorsStore
);

/**
 * Helper function to get a specific indicator from the current indicators data
 * @param indicatorKey The key of the indicator to retrieve (case-insensitive)
 * @returns The indicator data or null if not found
 */
export const getIndicator = (indicatorKey: string) => {
  return derived(indicators, ($indicators) => {
    if (!$indicators.data) return null;

    // Case-insensitive search
    const key = Object.keys($indicators.data).find(
      (k) => k.toLowerCase() === indicatorKey.toLowerCase()
    );

    return key ? $indicators.data[key] : null;
  });
};

/**
 * Helper function to extract time ranges where an indicator value is true (boolean)
 * or non-zero (number). It groups consecutive true/non-zero values into ranges.
 */
export function extractTimeRanges(indicatorData: IndicatorEntry[]): TimeRange[] {
  const ranges: TimeRange[] = [];
  let startDate: string | null = null;

  for (let i = 0; i < indicatorData.length; i++) {
    const current = indicatorData[i];
    // Check if value is "true" (boolean true or non-zero number)
    const isTrue =
      current.value === true || (typeof current.value === 'number' && current.value !== 0);

    if (isTrue) {
      if (startDate === null) {
        startDate = current.datetime;
      }
    } else {
      if (startDate !== null) {
        // End of a range. The previous point was the last "true" point.
        ranges.push({ startDate, endDate: indicatorData[i - 1].datetime });
        startDate = null;
      }
    }
  }

  // Handle case where the range extends to the end of the data
  if (startDate !== null) {
    ranges.push({ startDate, endDate: indicatorData[indicatorData.length - 1].datetime });
  }

  return ranges;
}

/**
 * Helper function to get time ranges for a specific boolean/flag indicator
 * @param indicatorKey The key of the indicator to retrieve
 */
export const getIndicatorTimeRanges = (indicatorKey: string) => {
  return derived(getIndicator(indicatorKey), ($indicatorData) => {
    if (!$indicatorData) return [];
    return extractTimeRanges($indicatorData);
  });
};

export const availableIndicators = derived(indicators, ($indicators) => {
  return $indicators.data ? Object.keys($indicators.data) : [];
});
