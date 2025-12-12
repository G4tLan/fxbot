<script lang="ts">
  import { page } from '$app/stores';
  import { backtestService } from '$lib/api/backtest.service';
  import type { BacktestResult, BacktestSessionResponse, TradeResult } from '$lib/api/types-helper';
  import BacktestResultView from '$lib/components/backtest/backtest-result-view.svelte';
  import { onMount } from 'svelte';

  let session = $state<BacktestSessionResponse | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);

  let result = $derived.by(() => {
    if (!session || !session.metrics) return null;

    // Map session data to BacktestResult expected by the view
    const metrics = session.metrics as Record<string, number>;

    return {
      initial_balance: metrics.initial_balance || 0,
      final_balance: metrics.final_balance || 0,
      pnl_percent: metrics.pnl_percent || 0,
      trades: (session.trades || []) as TradeResult[],
      closed_trades: [],
    } as BacktestResult;
  });

  onMount(async () => {
    const sessionId = $page.params.id;
    if (!sessionId) return;

    try {
      session = await backtestService.getSession(sessionId);
    } catch (e) {
      error = 'Failed to load session';
      console.error(e);
    } finally {
      loading = false;
    }
  });
</script>

<div class="mx-auto max-w-6xl">
  <div class="mb-6 flex items-center justify-between">
    <h2 class="text-2xl font-bold text-slate-100">Backtest Session</h2>
    <a href="/backtest/new" class="text-sm text-emerald-400 hover:text-emerald-300">
      ← New Backtest
    </a>
  </div>

  {#if loading}
    <div class="p-12 text-center text-slate-400">Loading session...</div>
  {:else if error}
    <div class="rounded-md bg-red-900/20 p-4 text-red-400">{error}</div>
  {:else if session}
    <div class="mb-8 rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <div class="mb-6 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div class="text-sm text-slate-500">Session ID</div>
          <div class="font-mono text-slate-200">{session.id}</div>
        </div>
        <div class="text-right">
          <div class="text-sm text-slate-500">Status</div>
          <span
            class="rounded px-2 py-1 text-xs font-medium"
            class:bg-green-900={session.status === 'completed'}
            class:text-green-400={session.status === 'completed'}
            class:bg-yellow-900={session.status === 'running'}
            class:text-yellow-400={session.status === 'running'}
            class:bg-red-900={session.status === 'failed'}
            class:text-red-400={session.status === 'failed'}
          >
            {session.status}
          </span>
        </div>
      </div>

      {#if result}
        <BacktestResultView {result} />
      {:else if session.status === 'running'}
        <div class="py-12 text-center">
          <div class="mb-4 text-xl text-slate-300">Backtest is running...</div>
          <div class="text-slate-500">Results will appear here once completed.</div>
        </div>
      {:else}
        <div class="py-12 text-center text-slate-500">No results available for this session.</div>
      {/if}
    </div>
  {/if}
</div>
