<script setup lang="ts">

// get borrowed items
const { data: borrowingsData } = await useFetch("/api/borrowings?active=true");
const borrowedItems = borrowingsData.value.loans.map(loan => loan["item"]);

// get owned items
const { data } = await useFetch("/api/myitems");

</script>

<template>
  <aside></aside>

  <main>

    <section class="title">
      <h1>Mes objets</h1>
      <p>Ici se trouvent tous les objets que vous possédez.</p>
    </section>

    <section>
      <div class="header">
        <h2>Mes objets</h2>
        <a role="button" href="/mystuff/new" class="bezel">Ajouter un objet</a>
      </div>
      <div class="content">
        <ItemExplorer :items="data.items" targetPrefix="/mystuff/" v-if="data.items.length" />
        <div class="empty" v-if="!data.items.length">You don't have any item yet</div>
      </div>
    </section>

    <section class="section" v-if="borrowedItems.length">
      <div class="header">
        <h2>Objets empruntés</h2>
      </div>
      <div class="content">
        <ItemExplorer :items="borrowedItems" targetPrefix="/explore/" />
      </div>
    </section>

  </main>

</template>

<style scoped>
.empty {
  text-align: center;
  color: var(--neutral-300);
}
</style>
