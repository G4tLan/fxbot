<script lang="ts">
  import BacktestConfigForm from '$lib/components/backtest/backtest-config-form.svelte';
  import TaskStatus from '$lib/components/common/task-status.svelte';
  import { taskStore } from '$lib/stores/task.store';
  import { onMount } from 'svelte';

  onMount(() => {
    taskStore.loadTasks();
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
        <h3 class="mb-4 text-lg font-medium text-slate-100">Recent Tasks</h3>
        <div class="space-y-4">
          {#each Object.values($taskStore.tasks)
            .filter((t) => t.type === 'backtest')
            .sort((a, b) => b.created_at - a.created_at)
            .slice(0, 5) as task (task.id)}
            <a
              href="/backtest/{task.id}"
              class="flex items-center justify-between rounded-md border border-slate-800 bg-slate-950/50 p-3 transition-colors hover:bg-slate-800"
            >
              <div>
                <div class="text-sm font-medium text-slate-200">Task #{task.id.slice(0, 8)}</div>
                <div class="text-xs text-slate-500">
                  {new Date(task.created_at * 1000).toLocaleString()}
                </div>
              </div>
              <TaskStatus status={task.status} />
            </a>
          {/each}
          {#if Object.values($taskStore.tasks).filter((t) => t.type === 'backtest').length === 0}
            <div class="text-center text-sm text-slate-500">No recent backtests</div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>
