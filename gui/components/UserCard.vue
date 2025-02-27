<script setup lang="ts">

import type { ApiResponse } from '#open-fetch';
import { ChevronRight } from 'lucide-vue-next';

type User = ApiResponse<'get_user_v1_users__user_id__get'>;

const props = defineProps<{
  user: User | null,
  target: string,
}>();

const { user, target } = toRefs(props);

const { name, avatarSeed, items, likesCount, starsCount, itemsCount } = useUser(user);

const router = useRouter();
const targetRoute = computed(() => user.value !== null ? router.resolve({ name: unref(target), params: { user_id: props.user?.id ?? 0 } }) : null);

</script>

<template>

  <div class="container">

    <NuxtLink :to="targetRoute ?? undefined">
      <div class="card" :title="name ?? undefined">
        <Avatar :seed="avatarSeed" />
        <span class="name">{{ name ?? "..." }}</span>
        <div class="counters">
          <Counter symbol="star" size="tiny" :count="starsCount" />
          <Counter symbol="heart" size="tiny" :count="likesCount" />
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
