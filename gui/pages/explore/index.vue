<script setup lang="ts">

const { data } = await useFetch("/api/items");

</script>

<template>
  <aside></aside>

  <main>

    <section class="title">
      <h1>Exploration</h1>
      <p>
        Trouve l'objet dont tu as besoin, demande le et profite !
      </p>
    </section>

    <section>
      <div class="content">
        <ItemExplorer :items="data.items" targetPrefix="/explore/" />
      </div>
    </section>

  </main>


</template>

<style scoped></style>
