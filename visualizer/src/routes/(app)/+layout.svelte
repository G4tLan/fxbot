<script lang="ts">
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth.store';
  import { onMount } from 'svelte';

  let { children } = $props();
  let checking = $state(true);

  onMount(() => {
    auth.init();
    if (!$auth.isAuthenticated) {
      goto('/login');
    }
    checking = false;
  });

  $effect(() => {
    if (!checking && !$auth.isAuthenticated) {
      goto('/login');
    }
  });
</script>

{#if checking}
  <div class="flex min-h-screen items-center justify-center bg-slate-950 text-slate-50">
    <p>Loading...</p>
  </div>
{:else if $auth.isAuthenticated}
  <div class="min-h-screen bg-slate-950 text-slate-50">
    <header class="border-b border-slate-800 bg-slate-900 p-4">
      <div class="flex items-center justify-between">
        <h1 class="text-xl font-bold text-emerald-400">FXBot Visualizer</h1>
        <button
          onclick={() => {
            auth.logout();
            goto('/login');
          }}
          class="text-sm text-slate-400 hover:text-white"
        >
          Logout
        </button>
      </div>
    </header>

    <main class="p-6">
      {@render children?.()}
    </main>
  </div>
{/if}
