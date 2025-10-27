<script lang="ts">
	import { tradeEngineService } from "$lib/api/trade-engine.service";
  import { selectedTicker, selectedInterval, selectedRun, selectedActiveTrade, selectedClosedTrade } from '$lib/stores';
	import type { TradeSummaryResponse } from "$lib/types";


  let trades = $state<TradeSummaryResponse | null>(null);

  $effect(() => {
    if ($selectedTicker && $selectedInterval && $selectedRun) {
      tradeEngineService.getTradeSummary($selectedTicker, $selectedInterval, $selectedRun).then((data) => {
        trades = data;
      });
    }
  });
</script>

{#if trades}

<input type="radio" id="tab-active" name="trade-tabs" hidden checked>
<input type="radio" id="tab-closed" name="trade-tabs" hidden>

<style>
  .panel { display: none; color: #000; }
  #tab-active:checked ~ .tabs label[for="tab-active"] {
    background-color: #22c55e; /* bright green (green-500) */
  }
  #tab-closed:checked ~ .tabs label[for="tab-closed"] {
    background-color: #e5e7eb; /* gray-200 */
  }
  #tab-active:checked ~ .panels #panel-active { display: block; color: #000; }
  #tab-closed:checked ~ .panels #panel-closed { display: block; color: #000; }
</style>

<div class="tabs flex gap-2 mb-2">
  <label
    class="px-3 py-1 rounded-md bg-green-800 text-black cursor-pointer font-semibold text-sm transition-colors duration-200"
    for="tab-active"
  >
    Active ({(trades.active_trades ?? []).length})
  </label>

  <label
    class="px-3 py-1 rounded-md bg-gray-700 text-black cursor-pointer font-semibold text-sm transition-colors duration-200"
    for="tab-closed"
  >
    Closed ({(trades.closed_trades ?? []).length})
  </label>
</div>

<div class="panels rounded-lg p-3 flex-1 w-full">
  <section id="panel-active" class="panel">
    {#if (trades.active_trades ?? []).length === 0}
      <p class="text-sm text-gray-500">No active trades.</p>
    {:else}
      <div class="list overflow-y-auto flex flex-col gap-2 h-full" role="list">
        {#each trades.active_trades ?? [] as t (t.entry_id)}
          <button 
            type="button"
            class="card flex flex-col gap-3 p-3 border rounded-md shadow-sm transition-colors duration-200 text-left w-full {$selectedActiveTrade?.entry_id === t.entry_id ? ' bg-gray-300': 'bg-white'}"
            onclick={() => selectedActiveTrade.set($selectedActiveTrade?.entry_id === t.entry_id ? null : t)}
            onkeydown={(e) => e.key === 'Enter' && selectedActiveTrade.set($selectedActiveTrade?.entry_id === t.entry_id ? null : t)}
            aria-pressed={$selectedActiveTrade?.entry_id === t.entry_id}
          >
            <div class="flex flex-row gap-2 justify-between">
              <div class="row flex items-center text-sm text-slate-800">
                <div class="px-2 py-1 rounded-full text-xs font-bold {t.type === 'BUY' ? 'bg-cyan-100 text-cyan-800' : 'bg-pink-100 text-pink-800'}">
                  {t.type}
                </div>
              </div>

              <div class="font-bold text-slate-900">
                Equity: {t.unrealised_pnl?.toFixed(2)}
              </div>
            </div>
            <div class="flex flex-col text-xs text-gray-500">
              <div>Entry: <span class="font-medium text-slate-700">{t.entry_price}</span></div>
              <div>SL: <span class="font-medium text-slate-700">{t.stop_loss}</span></div>
              <div>Opened: <span class="font-medium text-slate-700">{t.entry_datetime}</span></div>
            </div>
          </button>
        {/each}
      </div>
    {/if}
  </section>

  <section id="panel-closed" class="panel">
    {#if (trades.closed_trades ?? []).length === 0}
      <p class="text-sm text-gray-500">No closed trades.</p>
    {:else}
      <div class="list overflow-y-auto flex flex-col gap-3" role="list">
        {#each trades.closed_trades ?? [] as t (t.entry_id)}
          <button 
            type="button"
            class="card flex justify-between w-full items-center p-3 border rounded-md shadow-sm transition-colors duration-200 text-left {$selectedClosedTrade?.entry_id === t.entry_id ? ' bg-gray-300': 'bg-white'}"
            onclick={() => selectedClosedTrade.set($selectedClosedTrade?.entry_id === t.entry_id ? null : t)}
            onkeydown={(e) => e.key === 'Enter' && selectedClosedTrade.set($selectedClosedTrade?.entry_id === t.entry_id ? null : t)}
            aria-pressed={$selectedClosedTrade?.entry_id === t.entry_id}
          >
            <div class="flex flex-col gap-1 w-full">
              <div class="row flex justify-between items-center text-sm text-slate-800 min-w-0">
                <div class="px-2 py-1 rounded-full text-xs font-bold {t.type === 'BUY' ? 'bg-green-100 text-green-800' : 'bg-pink-100 text-pink-800'}">
                  {t.type}
                </div>

                <div class="text-right min-w-[140px]">
                  <div class="font-bold text-slate-900">
                    P&L: {t.profit}
                  </div>
                </div>
              </div>

              <div class="row flex justify-between text-xs text-gray-500">
                <div>Entry: <span class="font-medium text-slate-700">{t.entry_price}</span></div>
                <div>Exit: <span class="font-medium text-slate-700">{t.closed_price}</span></div>
              </div>

              <div class="flex-col flex text-xs text-gray-500">
                <div>Opened: <span class="font-medium text-slate-700">{t.entry_datetime}</span></div>
                <div>Closed: <span class="font-medium text-slate-700">{t.closed_datetime}</span></div>
              </div>
            </div>
          </button>
        {/each}
      </div>
    {/if}
  </section>
</div>

{:else}
  <p>No trade data available.</p>
{/if}