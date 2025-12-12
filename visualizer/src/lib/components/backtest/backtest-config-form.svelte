<script lang="ts">
  import { goto } from '$app/navigation';
  import { strategyService } from '$lib/api/strategy.service';
  import { backtestStore } from '$lib/stores/backtest.store';
  import { exchangeStore } from '$lib/stores/exchange.store';
  import { onMount } from 'svelte';

  let exchange = $state('');
  let symbol = $state('');
  let timeframe = $state('1h');
  let startDate = $state('');
  let endDate = $state('');
  let strategyName = $state('');
  let runInBackground = $state(true);
  let symbols: string[] = $state([]);
  let strategies: string[] = $state([]);

  const TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '4h', '1d'];

  onMount(async () => {
    loadStrategies();
    await exchangeStore.loadApiKeys();
    if ($exchangeStore.apiKeys.length > 0) {
      exchange = $exchangeStore.apiKeys[0].exchange_name;
      loadSymbols();
    }
  });

  async function loadStrategies() {
    try {
      const response = await strategyService.getStrategies();
      strategies = response.strategies;
      if (strategies.length > 0) {
        strategyName = strategies[0];
      }
    } catch (error) {
      console.error('Failed to load strategies', error);
    }
  }

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

    const response = await backtestStore.runBacktest({
      exchange,
      symbol,
      timeframe,
      start_date: startDate,
      end_date: endDate,
      strategy_name: strategyName,
      run_in_background: runInBackground,
    });

    if (response.task_id) {
      goto(`/backtest/${response.task_id}`);
    } else if (response.results) {
      goto('/backtest/result');
    }
  }
</script>

<div class="rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl">
  <h3 class="mb-6 text-lg font-medium text-slate-100">New Backtest</h3>

  <form onsubmit={handleSubmit} class="space-y-4">
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <!-- Exchange -->
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

      <!-- Symbol -->
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
      </div>

      <!-- Timeframe -->
      <div>
        <label for="timeframe" class="mb-1 block text-sm font-medium text-slate-400"
          >Timeframe</label
        >
        <select
          id="timeframe"
          bind:value={timeframe}
          class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        >
          {#each TIMEFRAMES as tf}
            <option value={tf}>{tf}</option>
          {/each}
        </select>
      </div>

      <!-- Strategy -->
      <div>
        <label for="strategy" class="mb-1 block text-sm font-medium text-slate-400">Strategy</label>
        <select
          id="strategy"
          bind:value={strategyName}
          class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        >
          {#each strategies as s}
            <option value={s}>{s}</option>
          {/each}
        </select>
      </div>

      <!-- Start Date -->
      <div>
        <label for="startDate" class="mb-1 block text-sm font-medium text-slate-400"
          >Start Date</label
        >
        <input
          type="date"
          id="startDate"
          bind:value={startDate}
          max={endDate}
          required
          class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        />
      </div>

      <!-- End Date -->
      <div>
        <label for="endDate" class="mb-1 block text-sm font-medium text-slate-400">End Date</label>
        <input
          type="date"
          id="endDate"
          bind:value={endDate}
          min={startDate}
          required
          class="w-full rounded-md border border-slate-700 bg-slate-800 px-3 py-2 text-slate-100 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 focus:outline-none"
        />
      </div>
    </div>

    <!-- Run in Background -->
    <div class="flex items-center space-x-2">
      <input
        type="checkbox"
        id="runInBackground"
        bind:checked={runInBackground}
        class="h-4 w-4 rounded border-slate-700 bg-slate-800 text-emerald-600 focus:ring-emerald-500"
      />
      <label for="runInBackground" class="text-sm font-medium text-slate-400"
        >Run in background</label
      >
    </div>

    <button
      type="submit"
      disabled={$backtestStore.loading || !exchange || !symbol || !startDate || !endDate}
      class="w-full rounded-md bg-emerald-600 px-4 py-2 font-medium text-white hover:bg-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:outline-none disabled:opacity-50"
    >
      {#if $backtestStore.loading}
        Starting Backtest...
      {:else}
        Run Backtest
      {/if}
    </button>
  </form>
</div>
