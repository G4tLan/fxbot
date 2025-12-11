<script lang="ts">
  import { toastStore } from '$lib/stores/toast.store';
  import Toast from './toast.svelte';
</script>

<div class="fixed right-5 bottom-5 z-50 flex flex-col gap-2">
  {#each $toastStore as toast (toast.id)}
    <Toast {toast} />
  {/each}
</div>
