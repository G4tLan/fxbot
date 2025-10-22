<script lang="ts">
  import { tradeEngineService } from '$lib/api/trade-engine.service';
  import { selectedTicker, selectedInterval, selectedRun, selectedDate } from '$lib/stores';
	import type { FiltersResponse } from '$lib/types';
  import { onMount } from 'svelte';

  let filters: FiltersResponse = [];
  let selectedTickerValue = '';
  let selectedIntervalValue = '';
  let selectedRunValue = '';
  let selectedDateValue = '';

  onMount(async () => {
    filters = await tradeEngineService.getFilters();
  });

  $: selectedTicker.set(selectedTickerValue);
  $: selectedInterval.set(selectedIntervalValue);
  $: selectedRun.set(selectedRunValue);
  $: selectedDate.set(selectedDateValue);
</script>

{#if filters.length}
  <label>Ticker:
    <select bind:value={selectedTickerValue}>
      {#each filters as f}
        <option value={f.ticker}>{f.ticker}</option>
      {/each}
    </select>
  </label>

  <label>Interval:
    <select bind:value={selectedIntervalValue}>
      {#each filters.find(f => f.ticker === selectedTickerValue)?.intervals ?? [] as i}
        <option value={i.interval}>{i.interval}</option>
      {/each}
    </select>
  </label>

  <label>Run:
    <select bind:value={selectedRunValue}>
      {#each filters.find(f => f.ticker === selectedTickerValue)?.intervals.find(i => i.interval === selectedIntervalValue)?.runs ?? [] as r}
        <option value={r.run_name}>{r.run_name}</option>
      {/each}
    </select>
  </label>

  <label>Date:
    <select bind:value={selectedDateValue}>
      {#each filters.find(f => f.ticker === selectedTickerValue)?.intervals.find(i => i.interval === selectedIntervalValue)?.runs.find(r => r.run_name === selectedRunValue)?.dates ?? [] as d}
        <option value={d}>{d}</option>
      {/each}
    </select>
  </label>
{/if}