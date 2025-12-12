<script lang="ts">
  import type { EquityHistoryEntry } from '$lib/types';
  import * as LC from 'lightweight-charts';
  import { onDestroy, onMount } from 'svelte';

  let { data = [] } = $props<{ data: EquityHistoryEntry[] }>();

  let chartContainer: HTMLElement;
  let chart: LC.IChartApi | null = null;
  let areaSeries: LC.ISeriesApi<'Area'> | null = null;

  function initChart() {
    if (!chartContainer) return;

    chart = LC.createChart(chartContainer, {
      layout: {
        background: { type: LC.ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8', // slate-400
      },
      grid: {
        vertLines: { color: '#1e293b' }, // slate-800
        horzLines: { color: '#1e293b' },
      },
      width: chartContainer.clientWidth,
      height: 300,
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    areaSeries = chart.addSeries(LC.AreaSeries, {
      lineColor: '#22c55e', // green-500
      topColor: 'rgba(34, 197, 94, 0.4)',
      bottomColor: 'rgba(34, 197, 94, 0.0)',
      lineWidth: 2,
    });

    updateChartData();

    window.addEventListener('resize', handleResize);
  }

  function updateChartData() {
    if (!areaSeries || !data.length) return;

    const chartData = data
      .map((entry: EquityHistoryEntry) => ({
        time: (new Date(entry.datetime).getTime() / 1000) as LC.Time,
        value: entry.equity,
      }))
      .sort(
        (a: { time: LC.Time }, b: { time: LC.Time }) => (a.time as number) - (b.time as number)
      );

    areaSeries.setData(chartData);
    chart?.timeScale().fitContent();
  }

  function handleResize() {
    if (chart && chartContainer) {
      chart.applyOptions({ width: chartContainer.clientWidth });
    }
  }

  onMount(() => {
    initChart();
  });

  onDestroy(() => {
    if (chart) {
      chart.remove();
      window.removeEventListener('resize', handleResize);
    }
  });

  $effect(() => {
    if (data) {
      updateChartData();
    }
  });
</script>

<div
  class="relative h-[300px] w-full rounded-lg border border-slate-800 bg-slate-900 p-4 shadow-xl"
>
  <h3 class="mb-2 text-sm font-medium text-slate-400">Equity Curve</h3>
  <div bind:this={chartContainer} class="h-full w-full"></div>
</div>
