<script lang="ts">
  import AddKeyModal from '$lib/components/exchange/add-key-modal.svelte';
  import ApiKeyList from '$lib/components/exchange/api-key-list.svelte';

  let isModalOpen = $state(false);
</script>

<div class="mx-auto max-w-4xl">
  <div class="mb-8 flex items-center justify-between">
    <div>
      <h2 class="text-2xl font-bold text-slate-100">Exchange Settings</h2>
      <p class="mt-1 text-slate-400">Manage your exchange API keys and configurations.</p>
    </div>
    <button
      onclick={() => (isModalOpen = true)}
      class="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-slate-900 focus:outline-none"
    >
      Add API Key
    </button>
  </div>

  <ApiKeyList />

  <AddKeyModal bind:isOpen={isModalOpen} />
</div>
