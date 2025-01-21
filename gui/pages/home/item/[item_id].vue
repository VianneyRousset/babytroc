<script setup lang="ts">

import { ArrowLeft, Ellipsis, Heart } from 'lucide-vue-next';

const { $api } = useNuxtApp()

const route = useRoute();

const itemId = computed(() => Number(route.params["item_id"]));

const { data: item, refresh: refreshItem } = await useApi('/v1/items/{item_id}', {
  path: {
    item_id: itemId,
  },
  key: `item/${itemId.value}`
});

const routeStack = useRouteStack();

const images = computed(() => {

  if (item.value === null)
    return [];

  return item.value.images_names.map((name: string) => `/api/v1/images/${name}`);

});

const likedItemsStore = useLikedItemsStore();
const liked = likedItemsStore.has(itemId) as ComputedRef<boolean>;
const likeLoading = ref(false);

async function toggleLike() {

  try {

    likeLoading.value = true;

    if (liked.value === true) {
      await likedItemsStore.remove(itemId.value);
    } else {
      await likedItemsStore.add(itemId.value);
    }

  } catch (error) {
    console.error(error);

    const { $toast } = useNuxtApp();

    $toast.error("Échec de la modification du like.");

  } finally {
    await refreshItem();
    likeLoading.value = false
  }
}

const loanRequestsStore = useLoanRequestsStore();
//const requested = loanRequestsStore.hasItem(itemId) as ComputedRef<boolean>;
const requestItemLoading = ref(false);

function timeout(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function requestItem() {

  try {

    requestItemLoading.value = true;

    await loanRequestsStore.requestItem(itemId.value);

  } catch (error) {
    console.error(error);

    const { $toast } = useNuxtApp();

    $toast.error("Échec de la demande d'emprunt.");

  } finally {
    requestItemLoading.value = false
  }

  await refreshItem();

}

const regionsIds = computed(() => item.value?.regions.map((reg) => reg.id) ?? []);


function formatedTargetedAge(ageMin: number | null, ageMax: number | null) {

  if (ageMin !== null && ageMin > 0) {

    if (ageMax === null)
      return `À partie de ${ageMin} mois`;

    return `De ${ageMin} à ${ageMax} mois`
  }

  if (ageMax !== null)
    return `Jusqu'à ${ageMax} mois`

  return "Pour tous âges"
}

</script>

<template>
  <div>

    <AppHeaderBar class="header-bar">
      <NuxtLink :to="routeStack.last.value ?? '/home'">
        <ArrowLeft style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </NuxtLink>
      <h1>{{ item?.name }}</h1>
      <Ellipsis style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />

    </AppHeaderBar>

    <div class="main">

      <div v-if="item !== null">

        <Gallery :images="item?.images_names ?? []" />

        <div style="padding-bottom: 1rem;">

          <div class="status">
            <Availability :available="item?.available ?? false" :loading="true" />

            <LikesCount :count="item?.likes_count ?? 0" :liked="liked" :loading="likeLoading" @click="toggleLike" />
          </div>

          <Fold title="Description">
            <p>{{ item.description }}</p>
          </Fold>

          <div style="margin-bottom: 2rem;">
            <Fold title="Détails">
              <div class="table">
                <div class="label">Âge</div>
                <div>{{ formatedTargetedAge(...item.targeted_age_months) }}</div>
                <div class="label">Régions</div>
                <ul>
                  <li v-for="region in item.regions">{{ region.name }}</li>
                </ul>
              </div>
              <RegionsMap style="width: 100%; height: auto;" :actives="item?.regions.map((reg) => reg.id) ?? []" />
            </Fold>
          </div>

          <Button type="bezel" :loading="requestItemLoading" @click="requestItem">Demander</Button>

        </div>
      </div>
    </div>

  </div>
</template>

<style scoped lang="scss">
.header-bar {

  @include flex-row;

  gap: 16px;
  height: 64px;

  a {
    @include flex-row;
  }

  svg {
    stroke: $neutral-700;
  }

  h1 {
    @include ellipsis-overflow;
    flex-grow: 1;

    font-weight: 500;
    font-size: 1.6rem;
  }

}

.main {
  padding: calc(64px + 1rem) 1rem;
  box-sizing: border-box;
  height: 100vh;
  overflow-y: scroll;
  color: $neutral-700;

  .status {
    @include flex-row;
    justify-content: space-between;
  }

  p {
    margin: 0;
  }

  .table {
    display: grid;
    gap: 1rem;
    grid-template-columns: 1fr 3fr;
    margin-bottom: 2rem;

    .label {
      color: $neutral-400;
    }

    ul {
      @include reset-list;
      @include flex-column;
      gap: 0.5rem;
      align-items: flex-start;

    }
  }
}
</style>
