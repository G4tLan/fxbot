<script lang="ts">
	import { onMount, } from 'svelte';
	import * as LC from 'lightweight-charts';
	import { tradeEngineService } from '$lib/api/trade-engine.service';
	import { selectedTicker, selectedInterval, selectedRun } from '$lib/stores';
	import { toZonedTime, format } from 'date-fns-tz';

	let chartContainer: HTMLElement;
	let chart: any = null;
	let candleSeries: any = null;
	// Guard for out-of-order async requests
	let _latestRequestId = 0;

	onMount(() => {
		chart = LC.createChart(chartContainer, {
			localization: {
				dateFormat: 'yyyy-MM-dd HH:mm',
				locale: 'en'
			},
			handleScale: {
				axisPressedMouseMove: {
					time: true,
					price: true
				}
			},
			layout: {
				background: { type: LC.ColorType.Solid, color: '#000000' },
				textColor: 'rgba(255, 255, 255, 0.95)',
			},
			grid: {
				vertLines: { color: 'rgba(197, 203, 206, 0.5)' },
				horzLines: { color: 'rgba(197, 203, 206, 0.5)' },
			},
			crosshair: { mode: 1 },
			rightPriceScale: { borderColor: 'rgba(197, 203, 206, 0.8)' },
			timeScale: {
				borderColor: 'rgba(197, 203, 206, 0.8)',
				timeVisible: true,
				secondsVisible: false,
				ticksVisible: true,
				tickMarkFormatter: (time: any, _tickType: any, locale: string) => {
					const date = new Date(time * 1000);
					switch (_tickType) {
						case LC.TickMarkType.DayOfMonth:
						case LC.TickMarkType.Month:
							return date.toLocaleDateString(locale, { month: 'short', year: 'numeric' });

						case LC.TickMarkType.Year:
							return date.toLocaleDateString(locale, { year: 'numeric' });

						case LC.TickMarkType.Time:
						default:
							// show hours and minutes for intraday ticks
							return date.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });
					}
				},
			}
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

		return () => {
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

				// round timestamps to a 5-minute grid (300s) so the time scale aligns to 5m intervals
				const INTERVAL_SEC = 5 * 60;
				const mapped = data.map((d) => {
					const dt = toZonedTime(new Date(d.datetime), 'UTC')
					return {
						time: (Math.floor(dt.getTime() / 1000 / INTERVAL_SEC) * INTERVAL_SEC) as LC.UTCTimestamp,
						open: d.Open,
						high: d.High,
						low: d.Low,
						close: d.Close
					};
				});

				candleSeries.setData(mapped);
				chart?.timeScale()?.fitContent();
			} catch (err) {
				console.error('Error loading candle data', err);
			}
		})();
	}
</script>

<div bind:this={chartContainer} class="w-full h-full"></div>
