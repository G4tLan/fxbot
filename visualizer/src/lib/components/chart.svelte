<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import * as LC from 'lightweight-charts';
	import { tradeEngineService } from '$lib/api/trade-engine.service';
	import { selectedTicker, selectedInterval, selectedRun } from '$lib/stores';

	let chartContainer: HTMLElement;
	let chart: any = null;
	let candleSeries: any = null;

	// ResizeObserver for responsive sizing
	let resizeObserver: ResizeObserver | null = null;

	// Guard for out-of-order async requests
	let _latestRequestId = 0;

	onMount(() => {
		const initialWidth = Math.max(1, Math.round(chartContainer.getBoundingClientRect().width));

		chart = LC.createChart(chartContainer, {
			width: initialWidth,
			height: 500,
			layout: {
				background: { type: LC.ColorType.Solid, color: '#000000' },
				textColor: 'rgba(255, 255, 255, 0.9)'
			},
			grid: {
				vertLines: { color: 'rgba(197, 203, 206, 0.5)' },
				horzLines: { color: 'rgba(197, 203, 206, 0.5)' }
			},
			crosshair: { mode: 1 },
			rightPriceScale: { borderColor: 'rgba(197, 203, 206, 0.8)' },
			timeScale: { borderColor: 'rgba(197, 203, 206, 0.8)' }
		});

		const seriesOptions = {
			upColor: '#26a69a',
			downColor: '#ef5350',
			borderDownColor: '#ef5350',
			borderUpColor: '#26a69a',
			wickDownColor: '#ef5350',
			wickUpColor: '#26a69a'
		};

		candleSeries = chart.addSeries(LC.CandlestickSeries, seriesOptions);

		if (window.ResizeObserver) {
			resizeObserver = new ResizeObserver((entries) => {
				for (const entry of entries) {
					const w = Math.max(1, Math.round(entry.contentRect.width));
					chart.applyOptions({ width: w });
				}
			});
			resizeObserver.observe(chartContainer);
		} else {
			const handleResize = () => chart.applyOptions({ width: Math.max(1, Math.round(chartContainer.getBoundingClientRect().width)) });
			window.addEventListener('resize', handleResize);
			onDestroy(() => window.removeEventListener('resize', handleResize));
		}

		return () => {
			if (resizeObserver) {
				resizeObserver.disconnect();
				resizeObserver = null;
			}
			if (chart) {
				chart.remove();
				chart = null;
			}
		};
	});

	// Reactive updates: fetch and set candle data when selections change
	$: if (candleSeries && $selectedTicker && $selectedInterval && $selectedRun) {
		const requestId = ++_latestRequestId;
		(async () => {
			try {
				const data = await tradeEngineService.getCandleData($selectedTicker, $selectedInterval, $selectedRun);
				if (requestId !== _latestRequestId) return; // stale

				const mapped = data.map((d) => ({
					time: Math.floor(new Date(d.datetime).getTime() / 1000) as any,
					open: d.Open,
					high: d.High,
					low: d.Low,
					close: d.Close
				}));

				candleSeries.setData(mapped);
				try { chart?.timeScale()?.fitContent(); } catch (e) {}
			} catch (err) {
				console.error('Error loading candle data', err);
			}
		})();
	}
</script>

<div bind:this={chartContainer} class="w-full h-[500px]"></div>
