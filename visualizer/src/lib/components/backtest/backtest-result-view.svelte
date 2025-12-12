<script lang="ts">
  import type { BacktestResult } from '$lib/api/types-helper';
  import Trades from '$lib/components/trades.svelte';

  let { result } = $props<{ result: BacktestResult }>();
</script>

<div class="space-y-6">
  <!-- Summary Metrics -->
  <div class="grid grid-cols-2 gap-4 md:grid-cols-4">
    <div class="rounded-md bg-slate-950 p-4">
      <div class="text-xs text-slate-500">Total Trades</div>
      <div class="text-xl font-bold text-slate-100">
        {result.trades.length}
      </div>
    </div>
    <div class="rounded-md bg-slate-950 p-4">
      <div class="text-xs text-slate-500">PnL %</div>
      <div class="text-xl font-bold text-slate-100">
        {(result.pnl_percent * 100).toFixed(2)}%
      </div>
    </div>
    <div class="rounded-md bg-slate-950 p-4">
      <div class="text-xs text-slate-500">Total PnL</div>
      <div
        class="text-xl font-bold"
        class:text-green-400={result.final_balance - result.initial_balance >= 0}
        class:text-red-400={result.final_balance - result.initial_balance < 0}
      >
        ${(result.final_balance - result.initial_balance).toFixed(2)}
      </div>
    </div>
    <div class="rounded-md bg-slate-950 p-4">
      <div class="text-xs text-slate-500">Final Balance</div>
      <div class="text-xl font-bold text-slate-100">
        ${result.final_balance.toFixed(2)}
      </div>
    </div>
  </div>

  <!-- Charts & Trades -->
  <div class="grid grid-cols-1 gap-6">
    <div class="lg:col-span-1">
      <Trades trades={result.trades ?? []} />
    </div>
  </div>

  <!-- JSON Dump (Collapsed by default or removed if confident) -->
  <details class="rounded-md bg-slate-950 p-4">
    <summary class="cursor-pointer text-sm font-medium text-slate-400">Raw Result Data</summary>
    <pre class="mt-2 max-h-96 overflow-auto text-xs text-slate-500">
      {JSON.stringify(result, null, 2)}
    </pre>
  </details>
</div>
