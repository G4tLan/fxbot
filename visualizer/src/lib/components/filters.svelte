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

<div class="filters">
  <div class="filter">
    <span>Ticker: </span>
    <select bind:value={selectedTickerValue}>
      {#each filters as f}
        <option value={f.ticker}>{f.ticker}</option>
      {/each}
    </select>
  </div>

  <div class="filter">
    <span>Interval: </span>
    <select bind:value={selectedIntervalValue}>
      {#each filters.find(f => f.ticker === selectedTickerValue)?.intervals ?? [] as i}
        <option value={i.interval}>{i.interval}</option>
      {/each}
    </select>
  </div>

  <div class="filter">
    <span>Run: </span>
    <select bind:value={selectedRunValue}>
      {#each filters.find(f => f.ticker === selectedTickerValue)?.intervals.find(i => i.interval === selectedIntervalValue)?.runs ?? [] as r}
        <option value={r.run_name}>{r.run_name}</option>
      {/each}
    </select>
  </div>

  <div class="filter">
    <span>Date: </span>
    <select bind:value={selectedDateValue}>
      {#each filters.find(f => f.ticker === selectedTickerValue)?.intervals.find(i => i.interval === selectedIntervalValue)?.runs.find(r => r.run_name === selectedRunValue)?.dates ?? [] as d}
        <option value={d}>{d}</option>
      {/each}
    </select>
  </div>
</div>

<style>
  .filters {
    display: flex;
    flex-direction: row;
    gap: 0.5rem;
  }

  .filter {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    min-width: 200px;
  }

  .filter span {
    font-weight: bold;
  }

  .filter select {
    padding: 0.5rem;
    border: 1px solid black;
    border-radius: 15px;
    color: black;
  }
</style>