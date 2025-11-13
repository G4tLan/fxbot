import { writable } from 'svelte/store';
import type { ActiveTrade, ClosedTrade } from '../types';

export const selectedTicker = writable<string | null>(null);
export const selectedInterval = writable<string | null>(null);
export const selectedRun = writable<string | null>(null);
export const selectedDate = writable<string | null>(null);

// Stores for selected trades
export const selectedActiveTrade = writable<ActiveTrade | null>(null);
export const selectedClosedTrade = writable<ClosedTrade | null>(null);
