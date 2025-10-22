import { writable } from 'svelte/store';

export const selectedTicker = writable('');
export const selectedInterval = writable('');
export const selectedRun = writable('');
export const selectedDate = writable('');