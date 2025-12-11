<script lang="ts">
  import favicon from '$lib/assets/favicon.svg';
  import ToastContainer from '$lib/components/ui/toast/toast-container.svelte';
  import { auth } from '$lib/stores/auth.store';
  import { onMount } from 'svelte';
  import '../app.css';

  let { children } = $props();

  onMount(() => {
    auth.init();
  });
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<ToastContainer />
{@render children?.()}
