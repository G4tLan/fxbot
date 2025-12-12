<script lang="ts">
  let { status } = $props<{ status: string }>();
</script>

{#if status === 'queued' || status === 'processing'}
  <span
    class="inline-flex items-center rounded-full bg-blue-900/30 px-2.5 py-0.5 text-xs font-medium text-blue-400"
  >
    <svg
      class="mr-1.5 h-2 w-2 animate-spin text-blue-400"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"
      ></circle>
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      ></path>
    </svg>
    {status}
  </span>
{:else if status === 'completed'}
  <span
    class="inline-flex items-center rounded-full bg-green-900/30 px-2.5 py-0.5 text-xs font-medium text-green-400"
  >
    Completed
  </span>
{:else if status === 'failed'}
  <span
    class="inline-flex items-center rounded-full bg-red-900/30 px-2.5 py-0.5 text-xs font-medium text-red-400"
  >
    Failed
  </span>
{:else}
  <span
    class="inline-flex items-center rounded-full bg-slate-800 px-2.5 py-0.5 text-xs font-medium text-slate-400"
  >
    {status}
  </span>
{/if}
