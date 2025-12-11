import { browser } from '$app/environment';
import { writable } from 'svelte/store';

// Types
export interface User {
  username: string;
  // Add other user properties as needed from the schema
}

export interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  user: User | null;
}

// Initial state
const initialState: AuthState = {
  token: null,
  isAuthenticated: false,
  user: null,
};

// Create the store
function createAuthStore() {
  const { subscribe, set, update } = writable<AuthState>(initialState);

  return {
    subscribe,
    login: (token: string, user: User) => {
      if (browser) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
      }
      set({ token, isAuthenticated: true, user });
    },
    logout: () => {
      if (browser) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
      set(initialState);
    },
    // Initialize from local storage
    init: () => {
      if (browser) {
        const token = localStorage.getItem('token');
        const userStr = localStorage.getItem('user');
        if (token && userStr) {
          try {
            const user = JSON.parse(userStr);
            set({ token, isAuthenticated: true, user });
          } catch (e) {
            console.error('Failed to parse user from local storage', e);
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            set(initialState);
          }
        }
      }
    },
  };
}

export const auth = createAuthStore();
