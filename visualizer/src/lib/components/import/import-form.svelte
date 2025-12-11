<script lang="ts">
  import { importService } from '$lib/api/import.service';
  import { exchangeStore } from '$lib/stores/exchange.store';
  import { taskStore } from '$lib/stores/task.store';
  import { toastStore } from '$lib/stores/toast.store';
  import { onMount } from 'svelte';

  let exchange = $state('');
  let symbol = $state('');
  let startDate = $state('');
  let loading = $state(false);
  let symbols: string[] = $state([]);

  onMount(async () => {
    await exchangeStore.loadApiKeys();
    if ($exchangeStore.apiKeys.length > 0) {
      exchange = $exchangeStore.apiKeys[0].exchange_name;
      loadSymbols();
    }
  });

  async function loadSymbols() {
    if (!exchange) return;
    symbols = await exchangeStore.loadSupportedSymbols(exchange);
    if (symbols.length > 0) {
      symbol = symbols[0];
    } else {
      symbol = '';
    }
  }

  async function handleSubmit(e: Event) {
    e.preventDefault();
    loading = true;

    try {
      const response = await importService.triggerImport({
        exchange,
        symbol,
        start_date: startDate,
      });

      taskStore.addImportTask(response);
      toastStore.success('Import started');
    } catch (error) {
      console.error(error);
    } finally {
      loading = false;
    }
  }
</script>

<div class="rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl">
  <h3 class="mb-6 text-lg font-medium text-slate-100">Import Data</h3>

  <form onsubmit={handleSubmit} class="space-y-4">
    <div>
      <label for="exchange" class="mb-1 block text-sm font-medium text-slate-400">Exchange</label>
      <select
        id="exchange"
        bind:value={exchange}
        onchange={loadSymbols}
        class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
      >
        {#each $exchangeStore.apiKeys as key}
          <option value={key.exchange_name}>{key.name} ({key.exchange_name})</option>
        {/each}
      </select>
    </div>

    <div>
      <label for="symbol" class="mb-1 block text-sm font-medium text-slate-400">Symbol</label>
      <div class="relative">
        <input
          type="text"
          id="symbol"
          bind:value={symbol}
          list="symbol-list"
          placeholder="e.g. EUR/USD"
          class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        />
        <datalist id="symbol-list">
          {#each symbols as s}
            <option value={s}></option>
          {/each}
        </datalist>
      </div>
      {#if symbols.length === 0 && exchange}
        <p class="mt-1 text-xs text-slate-500">
          No symbols found for this exchange. You can type one manually.
        </p>
      {/if}
    </div>

    <div>
      <label for="startDate" class="mb-1 block text-sm font-medium text-slate-400">Start Date</label
      >
      <input
        type="date"
        id="startDate"
        bind:value={startDate}
        required
        class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
      />
    </div>

    <button
      type="submit"
      disabled={loading || !exchange || !symbol || !startDate}
      class="w-full rounded-md bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:outline-none disabled:opacity-50"
    >
      {#if loading}
        Starting Import...
      {:else}
        Start Import
      {/if}
    </button>
  </form>
</div>
