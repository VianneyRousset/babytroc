<script setup lang="ts">
/**
 * Content on the side of the page.
 * Rendered as a Drawer in narrow window mode and mobile (c.f. useNarrowWindow).
 **/

const drawerOpen = defineModel<boolean>()

const props = defineProps<{
  position: 'left' | 'right'
  mode: 'panel' | 'drawer'
}>()

const { position, mode } = toRefs(props)
</script>

<template>
  <!-- panel mode (wide window) -->
  <Panel
    v-if="mode === 'panel'"
    class="PanelOrDrawer"
  >
    <template #header>
      <slot name="header" />
      <slot name="header-panel" />
    </template>
    <slot />
  </panel>

  <!-- drawer mode (wide window) -->
  <Teleport
    v-if="mode === 'drawer'"
    to="body"
  >
    <div class="PanelOrDrawer">
      <Overlay v-model="drawerOpen" />
      <Drawer
        v-model="drawerOpen"
        :position="position"
      >
        <Panel>
          <template #header>
            <slot name="header" />
            <slot name="header-drawer" />
          </template>
          <slot />
        </panel>
      </Drawer>
    </div>
  </Teleport>
</template>

<style scoped lang="scss">
</style>
