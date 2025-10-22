<script lang="ts">
	import { tradeEngineService } from "$lib/api/trade-engine.service";
	import type { TradeSummaryResponse } from "$lib/types";

  export let ticker: string;
  export let interval: string;
  export let run: string;
  let trades: TradeSummaryResponse;

  $: if (ticker && interval && run) {
    tradeEngineService.getTradeSummary(ticker, interval, run).then(data => trades = data);
  }
</script>

{#if trades}
  <pre>{JSON.stringify(trades, null, 2)}</pre>
{/if}