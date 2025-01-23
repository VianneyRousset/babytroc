<script setup lang="ts">

import type { ApiResponse } from '#open-fetch';
import { ChevronRight } from 'lucide-vue-next';

type User = ApiResponse<'get_user_v1_users__user_id__get'>;

const props = defineProps<{
  user?: User | null,
  loading?: boolean,
  target: string,
}>();

const loadingTimeout = ref(null as null | ReturnType<typeof setTimeout>);
const loader = ref(false);

watch(toRef(props, "loading"), (loading) => {

  if (loading) {

    if (loadingTimeout.value)
      clearTimeout(loadingTimeout.value);

    loadingTimeout.value = setTimeout(() => {
      loader.value = true
    }, 1000);

  } else {

    if (loadingTimeout.value)
      clearTimeout(loadingTimeout.value);

    loader.value = false;
  }

});

const router = useRouter();
const targetRoute = computed(() => router.resolve({ name: props.target, params: { user_id: 1 } }))

</script>

<template>

  <div class="container">
    <div v-if="props.loading" class="loading">
      <Loader :small="true" />
    </div>

    <NuxtLink :to="targetRoute">
      <div class="card" :title="props.user?.name ?? '...'">
        <Avatar :seed="props.user?.avatar_seed" />
        <span class="name">{{ props.user?.name ?? "..." }}</span>
        <div class="counters">
          <Counter symbol="star" size="tiny" :count="props.user?.stars_count" />
          <Counter symbol="heart" size="tiny" :count="props.user?.likes_count" />
        </div>
        <ChevronRight class="chevron" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      </div>
    </NuxtLink>
  </div>

</template>

<style scoped lang="scss">
a {
  @include reset-link;
}

.container {

  position: relative;

  .loading {
    @include flex-row-center;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
  }

  .card {
    @include flex-row;
    align-items: center;
    gap: 1.0rem;

    padding: 1.0rem 1.0rem;
    border-radius: 0.5rem;
    border: 1px solid $neutral-300;
    cursor: pointer;

    .avatar {
      width: 24px;

      background: gray;
    }

    .name {
      @include ellipsis-overflow;
      font-size: 1.6rem;
      padding-right: 10px;
      padding-bottom: 0.8rem;
      font-weight: 300;
      text-decoration: none;
    }

    .counters {
      @include flex-row;
      justify-content: right;
      gap: 0;
      position: absolute;
      bottom: 0.5rem;
      right: 1.0rem;

      ::v-deep div {
        color: $neutral-300;
      }
    }

    .chevron {
      position: absolute;
      top: calc(50% - 16px);
      right: 0.2rem;
      color: $neutral-300;
    }
  }
}
</style>
