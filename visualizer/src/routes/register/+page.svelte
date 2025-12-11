<script lang="ts">
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import type { MessageResponse, RegisterRequest } from '$lib/api/types-helper';
  import { toastStore } from '$lib/stores/toast.store';

  let username = $state('');
  let password = $state('');
  let email = $state('');
  let loading = $state(false);

  async function handleRegister(e: Event) {
    e.preventDefault();
    loading = true;

    try {
      const payload: RegisterRequest = {
        username,
        password,
        email: email || undefined,
      };

      await api.post<MessageResponse>('/api/v1/auth/register', payload);

      toastStore.success('Registration successful! Please login.');
      goto('/login');
    } catch (error) {
      console.error(error);
    } finally {
      loading = false;
    }
  }
</script>

<div class="flex min-h-screen items-center justify-center bg-slate-950 text-slate-50">
  <div class="w-full max-w-md rounded-lg border border-slate-800 bg-slate-900 p-8 shadow-xl">
    <h1 class="mb-6 text-center text-2xl font-bold text-emerald-400">Create Account</h1>

    <form onsubmit={handleRegister} class="space-y-6">
      <div>
        <label for="username" class="mb-2 block text-sm font-medium text-slate-400">Username</label>
        <input
          type="text"
          id="username"
          bind:value={username}
          required
          class="w-full rounded-md border border-slate-700 bg-slate-800 px-4 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        />
      </div>

      <div>
        <label for="email" class="mb-2 block text-sm font-medium text-slate-400"
          >Email (Optional)</label
        >
        <input
          type="email"
          id="email"
          bind:value={email}
          class="w-full rounded-md border border-slate-700 bg-slate-800 px-4 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        />
      </div>

      <div>
        <label for="password" class="mb-2 block text-sm font-medium text-slate-400">Password</label>
        <input
          type="password"
          id="password"
          bind:value={password}
          required
          class="w-full rounded-md border border-slate-700 bg-slate-800 px-4 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        class="w-full rounded-md bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-slate-900 focus:outline-none disabled:opacity-50"
      >
        {#if loading}
          Creating account...
        {:else}
          Register
        {/if}
      </button>

      <div class="text-center text-sm text-slate-400">
        Already have an account?
        <a href="/login" class="font-medium text-emerald-400 hover:text-emerald-300"> Login </a>
      </div>
    </form>
  </div>
</div>
