<script setup lang="ts" generic="T extends { name: string, avatar_seed: string, stars_count?: number, likes_count?: number}">
import { Heart, Star } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  user: T
  chevron?: boolean
}>(), {
  chevron: false,
})

const { user, chevron } = toRefs(props)
</script>

<template>
  <InfoBox
    class="UserCard"
    :chevron-right="chevron"
  >
    <template #icon>
      <UserAvatar :seed="user.avatar_seed" />
    </template>
    <template #mini>
      <StatsCounter
        v-model="user.stars_count"
        size="tiny"
      >
        <Heart
          :size="16"
          :stroke-width="1.33"
        />
      </StatsCounter>
      <StatsCounter
        v-model="user.likes_count"
        size="tiny"
      >
        <Star
          :size="16"
          :stroke-width="1.33"
        />
      </StatsCounter>
    </template>
    <span class="name">{{ user.name }}</span>
  </InfoBox>
</template>

<style scoped lang="scss">
.UserCard {
 .name {
    @include ellipsis-overflow;
    font-size: 1.6em;
    font-weight: 300;
  }
}
</style>
