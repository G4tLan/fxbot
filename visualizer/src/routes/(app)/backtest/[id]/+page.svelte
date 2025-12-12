<script lang="ts">
  import { page } from '$app/stores';
  import { taskService } from '$lib/api/task.service';
  import type { BacktestResult, Task } from '$lib/api/types-helper';
  import BacktestResultView from '$lib/components/backtest/backtest-result-view.svelte';
  import TaskStatus from '$lib/components/common/task-status.svelte';
  import { onMount } from 'svelte';

  let task = $state<Task | null>(null);
  let loading = $state(true);
  let error = $state<string | null>(null);

  let result = $derived(task?.result as unknown as BacktestResult | undefined);

  onMount(async () => {
    const taskId = $page.params.id;
    if (!taskId) return;

    try {
      task = await taskService.getTask(taskId);
    } catch (e) {
      error = 'Failed to load task';
      console.error(e);
    } finally {
      loading = false;
    }
  });
</script>

<div class="mx-auto max-w-6xl">
  <div class="mb-6 flex items-center justify-between">
    <h2 class="text-2xl font-bold text-slate-100">Backtest Result</h2>
    <a href="/backtest/new" class="text-sm text-emerald-400 hover:text-emerald-300">
      ← New Backtest
    </a>
  </div>

  {#if loading}
    <div class="p-12 text-center text-slate-400">Loading result...</div>
  {:else if error}
    <div class="rounded-md bg-red-900/20 p-4 text-red-400">{error}</div>
  {:else if task}
    <div class="mb-8 rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <div class="mb-6 flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div class="text-sm text-slate-500">Task ID</div>
          <div class="font-mono text-slate-200">{task.id}</div>
        </div>
        <div class="text-right">
          <div class="text-sm text-slate-500">Status</div>
          <TaskStatus status={task.status} />
        </div>
      </div>

      {#if task.status === 'completed' && result}
        <BacktestResultView {result} />
      {:else if task.status === 'failed'}
        <div class="rounded-md bg-red-900/20 p-4 text-red-400">
          <p class="font-bold">Backtest Failed</p>
          <p class="mt-1 text-sm">{task.error || 'Unknown error occurred'}</p>
        </div>
      {:else}
        <div class="p-8 text-center text-slate-400">
          <p>Backtest is currently {task.status}...</p>
        </div>
      {/if}
    </div>
  {/if}
</div>
