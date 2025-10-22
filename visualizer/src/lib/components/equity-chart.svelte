<script lang="ts">
  import { tradeEngineService } from '$lib/api/trade-engine.service';
  import { selectedTicker, selectedInterval, selectedRun } from '$lib/stores';
	import type { EquityHistoryEntry } from '$lib/types';
  import { onMount } from 'svelte';
  import { get } from 'svelte/store';

  let equityData: EquityHistoryEntry[] = [];

  async function loadEquity() {
    const ticker = get(selectedTicker);
    const interval = get(selectedInterval);
    const run = get(selectedRun);
    equityData = await tradeEngineService.getEquity(ticker, interval, run);
  }

  onMount(loadEquity);
</script>

<pre>{JSON.stringify(equityData, null, 2)}</pre>