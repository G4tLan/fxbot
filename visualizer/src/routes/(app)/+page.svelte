<script lang="ts">
  import Chart from '$lib/components/chart.svelte';
  import Filters from '$lib/components/filters.svelte';
  import Trades from '$lib/components/trades.svelte';
</script>

<div class="flex h-[calc(100vh-8rem)] flex-col gap-4">
  <section class="flex-none rounded-lg border border-slate-800 bg-slate-900 p-4">
    <Filters />
  </section>
  <div class="flex flex-1 flex-row gap-4 overflow-hidden">
    <section class="flex-1 rounded-lg border border-slate-800 bg-slate-900 p-4">
      <Chart />
    </section>
    <section
      class="w-1/4 flex-none overflow-auto rounded-lg border border-slate-800 bg-slate-900 p-4"
    >
      <Trades trades={[]} />
    </section>
  </div>
</div>
