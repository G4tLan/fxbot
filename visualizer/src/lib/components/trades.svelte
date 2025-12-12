<script lang="ts">
  import type { TradeResult } from '$lib/api/types-helper';

  let { trades = [] } = $props<{ trades: TradeResult[] }>();
</script>

<div
  class="h-[500px] w-full overflow-y-auto rounded-lg border border-slate-800 bg-slate-900 p-4 pt-0"
>
  <h3 class="mb-4 text-sm font-medium text-slate-400">Trade Executions</h3>
  <table class="w-full text-left text-sm text-slate-400">
    <thead class="sticky top-0 z-10 bg-slate-900 text-xs text-slate-500 uppercase shadow-sm">
      <tr>
        <th class="px-2 py-2">Time</th>
        <th class="px-2 py-2">Side</th>
        <th class="px-2 py-2 text-right">Price</th>
        <th class="px-2 py-2 text-right">Qty</th>
        <th class="px-2 py-2 text-right">Fee</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-slate-800">
      {#each trades as t}
        <tr class="hover:bg-slate-800/50">
          <td class="px-2 py-2 text-xs">{new Date(t.timestamp).toLocaleString()}</td>
          <td class="px-2 py-2">
            <span
              class="rounded px-1.5 py-0.5 text-xs font-bold {t.side.toLowerCase() === 'buy'
                ? 'bg-green-900/30 text-green-400'
                : 'bg-red-900/30 text-red-400'}"
            >
              {t.side}
            </span>
          </td>
          <td class="px-2 py-2 text-right font-mono text-slate-200">{t.price.toFixed(5)}</td>
          <td class="px-2 py-2 text-right font-mono">{t.qty}</td>
          <td class="px-2 py-2 text-right font-mono text-slate-500">{t.fee.toFixed(4)}</td>
        </tr>
      {/each}
    </tbody>
  </table>
</div>
