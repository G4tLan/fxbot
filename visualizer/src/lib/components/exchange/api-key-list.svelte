<script lang="ts">
  import { exchangeStore } from '$lib/stores/exchange.store';
  import { onMount } from 'svelte';

  onMount(() => {
    exchangeStore.loadApiKeys();
  });

  async function handleDelete(id: number) {
    if (confirm('Are you sure you want to delete this API key?')) {
      await exchangeStore.deleteApiKey(id);
    }
  }
</script>

<div class="overflow-hidden rounded-lg border border-slate-800 bg-slate-900">
  <div class="border-b border-slate-800 px-6 py-4">
    <h3 class="text-lg font-medium text-slate-100">Configured Exchanges</h3>
  </div>

  {#if $exchangeStore.loading && $exchangeStore.apiKeys.length === 0}
    <div class="p-8 text-center text-slate-400">Loading...</div>
  {:else if $exchangeStore.apiKeys.length === 0}
    <div class="p-8 text-center text-slate-400">No API keys configured.</div>
  {:else}
    <table class="w-full text-left text-sm text-slate-400">
      <thead class="bg-slate-950 text-xs text-slate-500 uppercase">
        <tr>
          <th class="px-6 py-3">Name</th>
          <th class="px-6 py-3">Exchange</th>
          <th class="px-6 py-3">API Key</th>
          <th class="px-6 py-3 text-right">Actions</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800">
        {#each $exchangeStore.apiKeys as key (key.id)}
          <tr class="hover:bg-slate-800/50">
            <td class="px-6 py-4 font-medium text-slate-200">{key.name}</td>
            <td class="px-6 py-4">
              <span
                class="inline-flex items-center rounded-full bg-blue-900/30 px-2.5 py-0.5 text-xs font-medium text-blue-400"
              >
                {key.exchange_name}
              </span>
            </td>
            <td class="px-6 py-4 font-mono text-xs">{key.api_key}</td>
            <td class="px-6 py-4 text-right">
              <button
                onclick={() => handleDelete(key.id)}
                class="font-medium text-red-400 hover:text-red-300 hover:underline"
              >
                Delete
              </button>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>
