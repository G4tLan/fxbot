<script lang="ts">
  import { toastStore, type Toast } from '$lib/stores/toast.store';
  import { fade, fly } from 'svelte/transition';

  export let toast: Toast;

  const bgColors = {
    success: 'bg-green-600',
    error: 'bg-red-600',
    info: 'bg-blue-600',
    warning: 'bg-yellow-600',
  };

  const icons = {
    success: '✓',
    error: '✕',
    info: 'ℹ',
    warning: '⚠',
  };
</script>

<div
  class="mb-4 flex w-full max-w-xs items-center rounded-lg p-4 text-white shadow-lg {bgColors[
    toast.type
  ]}"
  role="alert"
  in:fly={{ y: 20, duration: 300 }}
  out:fade={{ duration: 200 }}
>
  <div class="inline-flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-white/20">
    <span class="text-sm font-bold">{icons[toast.type]}</span>
  </div>
  <div class="ml-3 text-sm font-normal">{toast.message}</div>
  <button
    type="button"
    class="-mx-1.5 -my-1.5 ml-auto inline-flex h-8 w-8 items-center justify-center rounded-lg p-1.5 hover:bg-white/10 focus:ring-2 focus:ring-gray-300"
    aria-label="Close"
    on:click={() => toastStore.remove(toast.id)}
  >
    <span class="text-xl font-bold">×</span>
  </button>
</div>
