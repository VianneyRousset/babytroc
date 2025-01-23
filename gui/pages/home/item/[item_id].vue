<script setup lang="ts">

import { Ellipsis, Heart } from 'lucide-vue-next';
import { computedAsync } from '@vueuse/core'

const { $api } = useNuxtApp()

const route = useRoute();

const itemId = computed(() => Number(route.params["item_id"]));

const { data: item, refresh: refreshItem } = await useApi('/v1/items/{item_id}', {
  path: {
    item_id: itemId,
  },
  key: `item/${itemId.value}`
});


const images = computed(() => {

  if (item.value === null)
    return [];

  return item.value.images_names.map((name: string) => `/api/v1/images/${name}`);

});

const meStore = useMeStore();

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

const usersStore = useUsersStore();

const owner = computedAsync(async () => {

  if (item.value === null)
    return null;

  return await usersStore.get(item.value.owner.id);

});

const loanRequestsStore = useLoanRequestsStore();
const requested = loanRequestsStore.hasItem(itemId) as ComputedRef<boolean>;
const requestItemLoading = ref(false);

function timeout(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function requestItem() {

  // do not trigger request if already requested
  if (loanRequestsStore.hasItem(itemId.value))
    return;

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
      <AppBack fallback="/home" />
      <h1 :title="item?.name">{{ item?.name }}</h1>
      <Ellipsis style="cursor: pointer;" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />

    </AppHeaderBar>

    <div class="main">

      <Gallery :images="item?.images_names ?? []" />

      <div v-if="item !== null" class="info">

        <div>

          <div class="status">
            <Availability :available="item?.available ?? false" :loading="true" />
            <Counter symbol="heart" size="normal" :count="item?.likes_count ?? 0" :active="liked" :loading="likeLoading"
              @click="toggleLike" />
          </div>

          <Fold title="Description">
            <p>{{ item.description }}</p>
          </Fold>

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

        <ClientOnly>
          <UserCard :user="owner" target="home-user-user_id" />
        </ClientOnly>

        <Button type="bezel" v-if="item.owner_id !== meStore.me?.id" :loading="requestItemLoading" :disabled="requested"
          @click="requestItem">
          {{ requested ? "Demande envoyée" : "Demander" }}
        </Button>

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

  .info {
    @include flex-column;
    gap: 1rem;
    align-items: stretch;

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
}
</style>
