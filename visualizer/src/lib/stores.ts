import { writable } from 'svelte/store';
import type { ActiveTrade, ClosedTrade } from './types';

export const selectedTicker = writable('EURUSD=X');
export const selectedInterval = writable('5m');
export const selectedRun = writable('run-1');
export const selectedDate = writable('2025-10-20');

// Stores for selected trades
export const selectedActiveTrade = writable<ActiveTrade | null>(null);
export const selectedClosedTrade = writable<ClosedTrade | null>(null);