<script lang="ts">
  import type { StoreExchangeApiKeyRequest } from '$lib/api/types-helper';
  import { exchangeStore } from '$lib/stores/exchange.store';

  let { isOpen = $bindable(false) } = $props();

  let exchange_name = $state('binance');
  let name = $state('');
  let api_key = $state('');
  let api_secret = $state('');
  let loading = $state(false);

  const EXCHANGES = ['binance', 'kraken', 'kucoin', 'bybit'];

  async function handleSubmit(e: Event) {
    e.preventDefault();
    loading = true;

    const payload: StoreExchangeApiKeyRequest = {
      exchange_name,
      name,
      api_key,
      api_secret,
      additional_fields: null,
    };

    const success = await exchangeStore.addApiKey(payload);
    loading = false;

    if (success) {
      isOpen = false;
      // Reset form
      name = '';
      api_key = '';
      api_secret = '';
    }
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
    <div class="w-full max-w-md rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <div class="mb-6 flex items-center justify-between">
        <h3 class="text-lg font-medium text-slate-100">Add API Key</h3>
        <button onclick={() => (isOpen = false)} class="text-slate-400 hover:text-white">
          ✕
        </button>
      </div>

      <form onsubmit={handleSubmit} class="space-y-4">
        <div>
          <label for="exchange" class="mb-1 block text-sm font-medium text-slate-400"
            >Exchange</label
          >
          <select
            id="exchange"
            bind:value={exchange_name}
            class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
          >
            {#each EXCHANGES as ex}
              <option value={ex}>{ex.charAt(0).toUpperCase() + ex.slice(1)}</option>
            {/each}
          </select>
        </div>

        <div>
          <label for="name" class="mb-1 block text-sm font-medium text-slate-400"
            >Label (Name)</label
          >
          <input
            type="text"
            id="name"
            bind:value={name}
            required
            placeholder="e.g. My Binance Account"
            class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
          />
        </div>

        <div>
          <label for="api_key" class="mb-1 block text-sm font-medium text-slate-400">API Key</label>
          <input
            type="text"
            id="api_key"
            bind:value={api_key}
            required
            class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
          />
        </div>

        <div>
          <label for="api_secret" class="mb-1 block text-sm font-medium text-slate-400"
            >API Secret</label
          >
          <input
            type="password"
            id="api_secret"
            bind:value={api_secret}
            required
            class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
          />
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onclick={() => (isOpen = false)}
            class="rounded-md px-4 py-2 text-sm font-medium text-slate-300 hover:text-white"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            class="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:outline-none disabled:opacity-50"
          >
            {#if loading}
              Saving...
            {:else}
              Save API Key
            {/if}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
