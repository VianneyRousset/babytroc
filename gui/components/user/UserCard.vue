<script setup lang="ts">
import { ChevronRight, Heart, Star } from "lucide-vue-next";

const props = defineProps<{
	user: User;
}>();

const { user } = toRefs(props);
</script>

<template>
  <div class="UserCard" :title="user.name">
    <Avatar :seed="user.avatar_seed" />
    <span class="name">{{ user.name }}</span>
    <div class="counters">
      <Counter size="tiny" v-model="user.stars_count">
        <Heart :size="16" :strokeWidth="1.25" :absoluteStrokeWidth="true" />
      </Counter>
      <Counter size="tiny" v-model="user.likes_count">
        <Star :size="16" :strokeWidth="1.25" :absoluteStrokeWidth="true" />
      </Counter>
    </div>
    <ChevronRight class="chevron" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
  </div>
</template>

<style scoped lang="scss">
.UserCard {

  @include reset-link;
  @include flex-row;
  align-items: center;
  gap: 1.0rem;

  position: relative;

  color: $neutral-700 !important;
  text-decoration: none !important;

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
  }

  .counters {
    @include flex-row;
    justify-content: right;
    gap: 0;
    position: absolute;
    bottom: 0.5rem;
    right: 1.0rem;

    :deep(div) {
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
</style>
