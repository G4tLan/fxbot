<script lang="ts">
  import { tradeEngineService } from '$lib/api/trade-engine.service';
  import { TradePrimitive } from '$lib/indicators/trade-primitive';
  import {
    selectedActiveTrade,
    selectedClosedTrade,
    selectedInterval,
    selectedRun,
    selectedTicker,
  } from '$lib/stores';
  import { timeZoneCorrection } from '$lib/utils';
  import * as LC from 'lightweight-charts';
  import { onMount } from 'svelte';

  let chartContainer: HTMLElement;
  let chart: any = null;
  let candleSeries: any = null;
  let tradePrimitive: TradePrimitive;
  // Guard for out-of-order async requests
  let _latestRequestId = 0;

  onMount(() => {
    chart = LC.createChart(chartContainer, {
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
    tradePrimitive = new TradePrimitive(candleSeries);

    candleSeries.attachPrimitive(tradePrimitive);

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

          // round timestamps to a 5-minute grid (300s) so the time scale aligns to 5m intervals
          const INTERVAL_SEC = 5 * 60;
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
</script>

<div bind:this={chartContainer} class="h-full w-full"></div>
