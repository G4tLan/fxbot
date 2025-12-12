<script lang="ts">
  import type { BacktestResult } from '$lib/api/types-helper';
  import BacktestResultView from '$lib/components/backtest/backtest-result-view.svelte';
  import { backtestStore } from '$lib/stores/backtest.store';
  import { onMount } from 'svelte';

  let result = $state<BacktestResult | null>(null);

  onMount(() => {
    // Try to get result from store
    if ($backtestStore.lastResult?.results) {
      result = $backtestStore.lastResult.results;
    }
  });
</script>

<div class="mx-auto max-w-6xl">
  <div class="mb-6 flex items-center justify-between">
    <h2 class="text-2xl font-bold text-slate-100">Latest Backtest Result</h2>
    <a href="/backtest/new" class="text-sm text-emerald-400 hover:text-emerald-300">
      ← New Backtest
    </a>
  </div>

  {#if result}
    <div class="mb-8 rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <BacktestResultView {result} />
    </div>
  {:else}
    <div class="p-12 text-center text-slate-400">
      <p>No recent backtest result found.</p>
      <a href="/backtest/new" class="mt-4 inline-block text-emerald-400 hover:text-emerald-300">
        Start a new backtest
      </a>
    </div>
  {/if}
</div>
