<script lang="ts">
  import BacktestConfigForm from '$lib/components/backtest/backtest-config-form.svelte';
  import { backtestStore } from '$lib/stores/backtest.store';
  import { onMount } from 'svelte';

  onMount(() => {
    backtestStore.loadSessions({ page: 1, limit: 5, offset: 0 });
  });
</script>

<div class="mx-auto max-w-4xl">
  <div class="mb-8">
    <h2 class="text-2xl font-bold text-slate-100">Backtest Execution</h2>
    <p class="mt-1 text-slate-400">Configure and run a new backtest strategy.</p>
  </div>

  <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
    <div class="lg:col-span-2">
      <BacktestConfigForm />
    </div>

    <div>
      <div class="rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl">
        <h3 class="mb-4 text-lg font-medium text-slate-100">Recent Sessions</h3>
        <div class="space-y-4">
          {#each $backtestStore.sessions as session (session.id)}
            <a
              href="/backtest/{session.id}"
              class="flex items-center justify-between rounded-md border border-slate-800 bg-slate-950/50 p-3 transition-colors hover:bg-slate-800"
            >
              <div>
                <div class="text-sm font-medium text-slate-200">
                  {session.title || `Session #${session.id.slice(0, 8)}`}
                </div>
                <div class="text-xs text-slate-500">
                  {new Date(session.created_at * 1000).toLocaleString()}
                </div>
              </div>
              <span
                class="rounded px-2 py-1 text-xs font-medium"
                class:bg-green-900={session.status === 'completed'}
                class:text-green-400={session.status === 'completed'}
                class:bg-yellow-900={session.status === 'running'}
                class:text-yellow-400={session.status === 'running'}
                class:bg-red-900={session.status === 'failed'}
                class:text-red-400={session.status === 'failed'}
                class:bg-slate-800={!['completed', 'running', 'failed'].includes(session.status)}
                class:text-slate-300={!['completed', 'running', 'failed'].includes(session.status)}
              >
                {session.status}
              </span>
            </a>
          {/each}
          {#if $backtestStore.sessions.length === 0}
            <div class="text-center text-sm text-slate-500">No recent sessions</div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>
