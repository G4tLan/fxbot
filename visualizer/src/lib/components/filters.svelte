<script lang="ts">
    import { tradeEngineService } from '$lib/api/trade-engine.service';
    import type { FiltersResponse } from '$lib/types';
  import { onMount } from 'svelte';
  let filters: FiltersResponse = [];

  onMount(async () => {
    filters = await tradeEngineService.getFilters();
    console.log(filters);

  });
</script>

<pre>{JSON.stringify(filters, null, 2)}</pre>