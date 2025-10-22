<script setup lang="ts">
const drawerOpen = defineModel<boolean>()

const props = withDefaults(defineProps<{
  position: 'left' | 'right'
  drawer: boolean
  page?: boolean
}>(), {
  page: true,
})

const { position, drawer, page } = toRefs(props)
</script>

<template>
  <!-- Drawer mode -->
  <Teleport
    v-if="drawer"
    to="body"
    :disabled="!page"
  >
    <div
      class="ConditionalDrawer"
      :class="{ page }"
    >
      <Overlay v-model="drawerOpen" />
      <Drawer
        v-model="drawerOpen"
        :position="position"
      >
        <slot name="drawer-only" />
        <slot />
      </Drawer>
    </div>
  </Teleport>

  <!-- panel mode (wide window) -->
  <div
    v-else
    class="ConditionalDrawer"
  >
    <slot name="panel-only" />
    <slot />
  </div>
</template>

<style scoped lang="scss">
.ConditionalDrawer {
  &:not(.page) {
    .Overlay {
      position: absolute;
    }

    .Drawer {
      position: absolute;
    }
  }
}
</style>
