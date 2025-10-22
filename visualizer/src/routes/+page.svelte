<script lang="ts">
  import Filters from '$lib/components/filters.svelte';
  import Trades from '$lib/components/trades.svelte';
  import EquityChart from '$lib/components/equity-chart.svelte';
  import CandlesTable from '$lib/components/candles-table.svelte';
  import Payloads from '$lib/components/payloads.svelte';

  let ticker = 'EURUSD=X';
  let interval = '5m';
  let run = 'run-1';
  let date = '2025-10-20';
</script>

<h1>Backtest Visualizer</h1>
<Filters />

