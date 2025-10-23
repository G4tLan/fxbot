<script lang="ts">
  import Filters from '$lib/components/filters.svelte';
  import Chart from '$lib/components/chart.svelte';
  import Payloads from '$lib/components/payloads.svelte';
</script>

<div class="dashboard">
  <section class="filters"><Filters /></section>
  <section class="chart"><Chart /></section>
  <section class="details"><Payloads /></section>
</div>

<style>
  .dashboard {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: #111;
    color: white;
    font-family: sans-serif;
    padding: 1rem;
    gap: 1rem;
  }

  section {
    border: 1px solid white;
    padding: 0.5rem;
    overflow: auto;
  }

  .filters {
    flex: 0 0 auto;
  }

  .chart {
    flex: 1 1 auto;
  }

  .details {
    flex: 0 0 15%;
  }
</style>