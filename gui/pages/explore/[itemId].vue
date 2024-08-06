<script setup lang="ts">

const route = useRoute();
const itemId = route.params.itemId;

const { data, refresh } = await useFetch(`/api/items/${itemId}`);

async function request() {

  await $fetch(`/api/items/${itemId}/request`, {
    method: "POST",
  })

  await refresh();

}

</script>

<template>
  <main class="narrow">

    <section>
      <div class="content row">
        <ItemPreview :item="data?.item" class="img" />
        <div class="info">
          <div>
            <h2>{{ data?.item.name }}</h2>
            <div class="owner">
              <UserThumb :user="data?.item.owner" :size=40 />{{ data?.item.owner.name }}
            </div>
            <p>{{ data?.item.description }}</p>
          </div>
          <button class="flat" @click="request()" :disabled="data?.item.requested">
            {{ data?.item.requested ? "Demandé" : "Demander l'objet" }}
          </button>
        </div>
      </div>
    </section>

  </main>
</template>

<style scoped>
.info {
  display: flex;
  flex-direction: column;
}

.img {
  width: 24rem;
  height: 24rem;
}

.owner {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: var(--neutral-800);
  font-weight: 500;
  font-size: 1.2rem;
}


h2 {
  font-weight: medium;
  font-size: 2rem;
  color: var(--neutral-800);
  margin: 0;
  margin-bottom: 1rem;
}

p {
  color: var(--neutral-500);
  font-size: 1.2rem;
}

@media only screen and (max-width: 50rem) {

  .img {
    width: 100%;
  }
}
</style>
