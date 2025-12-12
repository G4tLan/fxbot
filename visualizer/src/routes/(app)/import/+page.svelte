<script lang="ts">
  import TaskStatus from '$lib/components/common/task-status.svelte';
  import ImportForm from '$lib/components/import/import-form.svelte';
  import { taskStore } from '$lib/stores/task.store';
  import { onMount } from 'svelte';

  onMount(() => {
    taskStore.loadTasks();
  });
</script>

<div class="mx-auto max-w-4xl">
  <div class="mb-8">
    <h2 class="text-2xl font-bold text-slate-100">Data Import</h2>
    <p class="mt-1 text-slate-400">Import historical candle data for backtesting.</p>
  </div>

  <div class="grid gap-8 md:grid-cols-2">
    <div>
      <ImportForm />
    </div>

    <div class="rounded-lg border border-slate-800 bg-slate-900 p-6 shadow-xl">
      <h3 class="mb-6 text-lg font-medium text-slate-100">Recent Tasks</h3>

      <div class="space-y-4">
        {#each Object.values($taskStore.tasks).sort((a, b) => (b.created_at || 0) - (a.created_at || 0)) as task}
          <div
            class="flex items-center justify-between rounded-md border border-slate-800 bg-slate-950 p-4"
          >
            <div>
              <div class="text-sm font-medium text-slate-200">
                Task {task.id.slice(0, 8)}...
              </div>
              <div class="text-xs text-slate-500">
                {task.created_at ? new Date(task.created_at * 1000).toLocaleString() : 'Just now'}
              </div>
            </div>
            <div>
              <TaskStatus status={task.status} />
            </div>
          </div>
        {/each}

        {#if Object.keys($taskStore.tasks).length === 0}
          <div class="text-center text-sm text-slate-500">No tasks found.</div>
        {/if}
      </div>
    </div>
  </div>
</div>
