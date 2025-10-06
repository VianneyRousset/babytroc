<script setup lang="ts" generic="T extends { name: string, avatar_seed: string, stars_count?: number, likes_count?: number}">
import { Heart, Star } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const props = defineProps<{
  user: T
  target?: string | RouteLocationGeneric | ((userId: number) => string | RouteLocationGeneric)
}>()
const { user, target } = toRefs(props)

const targetLocation = computed<string | RouteLocationGeneric | undefined>(() => {
  const _target = unref(target)

  if (_target == null)
    return undefined

  if (typeof _target === 'function')
    return _target(unref(user).id)

  return _target
})
</script>

<template>
  <InfoBox
    class="UserCard"
    :chevron-right="targetLocation != null"
    :target="targetLocation"
  >
    <template #icon>
      <UserAvatar :seed="user.avatar_seed" />
    </template>
    <template #mini>
      <HorizontalCounter
        v-model="user.stars_count"
        size="tiny"
      >
        <Heart
          :size="16"
          :stroke-width="1.33"
        />
      </HorizontalCounter>
      <HorizontalCounter
        v-model="user.likes_count"
        size="tiny"
      >
        <Star
          :size="16"
          :stroke-width="1.33"
        />
      </HorizontalCounter>
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
