import { writable } from 'svelte/store';

export const selectedTicker = writable('EURUSD=X');
export const selectedInterval = writable('5m');
export const selectedRun = writable('run-1');
export const selectedDate = writable('2025-10-20');