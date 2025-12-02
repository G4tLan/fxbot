<script lang="ts">
  import { tradeEngineService } from '$lib/api/trade-engine.service';
  import { ConsolidationPrimitive } from '$lib/indicators/consolidation-primitive';
  import { TradePrimitive } from '$lib/indicators/trade-primitive';
  import {
    selectedActiveTrade,
    selectedClosedTrade,
    selectedInterval,
    selectedRun,
    selectedTicker,
  } from '$lib/stores';
  import { indicatorsStore, type IndicatorsStore } from '$lib/stores/indicators';
  import { INTERVAL_SEC, timeZoneCorrection } from '$lib/utils';
  import * as LC from 'lightweight-charts';
  import { onMount } from 'svelte';

  let chartContainer: HTMLElement;
  let chart: LC.IChartApi | null = null;
  let candleSeries: LC.ISeriesApi<'Candlestick'> | null = null;
  let emaLongSeries: LC.ISeriesApi<'Line'> | null = null;
  let emaShortSeries: LC.ISeriesApi<'Line'> | null = null;
  let tradePrimitive: TradePrimitive;
  let consolidationPrimitive: ConsolidationPrimitive;

  // Reactive indicators state
  let indicatorsState = $state<IndicatorsStore>({ data: null, loading: false, error: null });
  let candleData = $state<any[]>([]);

  // Guard for out-of-order async requests
  let _latestRequestId = 0; // Track window dimensions
  let windowWidth = $state(0);
  let windowHeight = $state(0);

  // Handle window resize
  $effect(() => {
    if (typeof window !== 'undefined' && chart && chartContainer) {
      const container = chartContainer.getBoundingClientRect();
      chart.applyOptions({
        width: container.width,
        height: container.height,
      });
    }
  });

  onMount(() => {
    const container = chartContainer.getBoundingClientRect();
    chart = LC.createChart(chartContainer, {
      width: container.width,
      height: container.height,
      localization: {
        dateFormat: 'yyyy-MM-dd',
        locale: 'en',
        priceFormatter: (p: number) => p.toFixed(5),
      },
      handleScale: {
        axisPressedMouseMove: {
          time: true,
          price: true,
        },
      },
      layout: {
        background: { type: LC.ColorType.Solid, color: '#fff' },
        textColor: 'rgba(0, 0, 0, 0.95)',
      },
      grid: {
        vertLines: { color: 'rgba(197, 203, 206, 0.5)' },
        horzLines: { color: 'rgba(197, 203, 206, 0.5)' },
      },
      crosshair: {
        mode: LC.CrosshairMode.Normal,
        vertLine: {
          width: 4 as any,
          color: '#C3BCDB44',
          style: LC.LineStyle.Solid,
          labelBackgroundColor: '#9B7DFF',
        },

        horzLine: {
          color: '#9B7DFF',
          labelBackgroundColor: '#9B7DFF',
        },
      },
      rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 1.0)',
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
        mode: LC.PriceScaleMode.Logarithmic,
      },
      timeScale: {
        borderColor: 'rgba(197, 203, 206, 1.0)',
        timeVisible: true,
        secondsVisible: false,
        ticksVisible: true,
        tickMarkFormatter: (time: any, _tickType: any, locale: string) => {
          const date = new Date(time * 1000);
          switch (_tickType) {
            case LC.TickMarkType.DayOfMonth:
              return date.toLocaleDateString(locale, { month: 'short', day: 'numeric' });
            case LC.TickMarkType.Month:
              return date.toLocaleDateString(locale, { month: 'short', year: 'numeric' });

            case LC.TickMarkType.Year:
              return date.toLocaleDateString(locale, { year: 'numeric' });

            case LC.TickMarkType.Time:
            default:
              return date.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' });
          }
        },
      },
    });

    const seriesOptions = {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderDownColor: '#ef5350',
      borderUpColor: '#26a69a',
      wickDownColor: '#ef5350',
      wickUpColor: '#26a69a',
    };

    candleSeries = chart.addSeries(LC.CandlestickSeries, seriesOptions);
    emaLongSeries = chart.addSeries(LC.LineSeries, {
      color: 'blue',
      lineWidth: 1,
      crosshairMarkerVisible: false,
      lastValueVisible: false,
      priceLineVisible: false,
    });
    emaShortSeries = chart.addSeries(LC.LineSeries, {
      color: 'red',
      lineWidth: 1,
      crosshairMarkerVisible: false,
      lastValueVisible: false,
      priceLineVisible: false,
    });
    tradePrimitive = new TradePrimitive(candleSeries);
    consolidationPrimitive = new ConsolidationPrimitive(candleSeries, {
      color: 'rgba(255, 165, 0, 0.3)',
    });

    candleSeries.attachPrimitive(tradePrimitive);
    candleSeries.attachPrimitive(consolidationPrimitive);

    return () => {
      if (chart) {
        chart.remove();
        chart = null;
      }
    };
  });

  // Reactive updates: fetch and set candle data when selections change
  $effect(() => {
    if (candleSeries && $selectedTicker && $selectedInterval && $selectedRun) {
      const requestId = ++_latestRequestId;

      (async () => {
        try {
          const data = await tradeEngineService.getCandleData(
            $selectedTicker,
            $selectedInterval,
            $selectedRun
          );
          if (requestId !== _latestRequestId) return; // stale

          const mapped = data.map((d) => {
            return {
              time: (Math.floor(timeZoneCorrection(d.datetime) / INTERVAL_SEC) *
                INTERVAL_SEC) as LC.UTCTimestamp,
              open: d.Open,
              high: d.High,
              low: d.Low,
              close: d.Close,
            };
          });

          candleData = mapped;
          candleSeries.setData(mapped);
          chart?.timeScale()?.fitContent();
        } catch (err) {
          console.error('Error loading candle data', err);
        }
      })();
    }
  });

  $effect(() => {
    if ($selectedActiveTrade) {
      tradePrimitive.setPoints({
        entryTime: Math.floor(timeZoneCorrection($selectedActiveTrade.entry_datetime)) as LC.Time,
        entryPrice: $selectedActiveTrade.entry_price,
        stopLoss: $selectedActiveTrade.stop_loss,
        takeProfit: $selectedActiveTrade.take_profit,
        inProfit: !!$selectedActiveTrade.unrealised_pnl && $selectedActiveTrade.unrealised_pnl > 0,
      });
    } else if ($selectedClosedTrade) {
      tradePrimitive.setPoints({
        entryTime: Math.floor(timeZoneCorrection($selectedClosedTrade.entry_datetime)) as LC.Time,
        entryPrice: $selectedClosedTrade.entry_price,
        stopLoss: $selectedClosedTrade.stop_loss,
        takeProfit: $selectedClosedTrade.take_profit,
        closePrice: $selectedClosedTrade.closed_price,
        inProfit: !!$selectedClosedTrade.profit && $selectedClosedTrade.profit > 0,
        closeTime: Math.floor(timeZoneCorrection($selectedClosedTrade.closed_datetime)) as LC.Time,
      });
    } else {
      tradePrimitive.setPoints(null);
    }
  });

  $effect(() => {
    const unsubscribe = indicatorsStore.subscribe((value) => {
      if (value.processedData && value.processedData['consolidation']) {
        if (consolidationPrimitive && candleData.length > 0) {
          consolidationPrimitive.setData(value.processedData['consolidation'], candleData);
        }
      }

      if (emaLongSeries && value.processedData && value.processedData['ema_long']) {
        emaLongSeries.setData(value.processedData['ema_long']);
      }
      if (emaShortSeries && value.processedData && value.processedData['ema_short']) {
        emaShortSeries.setData(value.processedData['ema_short']);
      }
      indicatorsState = value;
    });
    if (candleSeries && $selectedTicker && $selectedInterval && $selectedRun) {
      indicatorsStore.fetchIndicators($selectedTicker, $selectedInterval, $selectedRun);
    }

    return unsubscribe;
  });
</script>

<svelte:window bind:innerWidth={windowWidth} bind:innerHeight={windowHeight} />

<div class="relative h-full min-h-[400px] w-full">
  <div bind:this={chartContainer} class="h-full w-full"></div>

  <!-- Indicators Status Overlay -->
  {#snippet indicatorsStatus()}
    <div
      class="absolute top-2 right-2 rounded-lg bg-white/90 p-2 text-xs shadow-sm backdrop-blur-sm"
    >
      <div class="flex items-center gap-2">
        {#if indicatorsState.loading}
          <div class="h-2 w-2 animate-pulse rounded-full bg-blue-500"></div>
          <span>Loading indicators...</span>
        {:else if indicatorsState.error}
          <div class="h-2 w-2 rounded-full bg-red-500"></div>
          <span class="text-red-600">Error: {indicatorsState.error}</span>
        {:else if indicatorsState.data}
          <div class="h-2 w-2 rounded-full bg-green-500"></div>
          <span>{Object.keys(indicatorsState.data).length} indicators loaded</span>
        {:else}
          <div class="h-2 w-2 rounded-full bg-gray-400"></div>
          <span>No indicators</span>
        {/if}
      </div>

      <!-- Show available indicators when loaded -->
      {#if indicatorsState.data && Object.keys(indicatorsState.data).length > 0}
        <div class="mt-1 text-xs text-gray-600">
          {Object.keys(indicatorsState.data).join(', ')}
        </div>
      {/if}
    </div>
  {/snippet}

  {@render indicatorsStatus()}
</div>
