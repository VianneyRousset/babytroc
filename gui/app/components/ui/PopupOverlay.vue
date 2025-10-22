<script setup lang="ts">
const model = defineModel<boolean>()

const props = withDefaults(defineProps<{
  page?: boolean
}>(), {
  page: true,
})

const { page } = toRefs(props)
const slots = useSlots()
</script>

<template>
  <Teleport
    to="body"
    :disabled="!page"
  >
    <div
      class="PopupOverlay"
      :class="{ page }"
    >
      <Overlay v-model="model">
        <Popup v-model="model">
          <slot />
          <template
            v-if="slots.actions"
            #actions
          >
            <slot name="actions" />
          </template>
        </Popup>
      </Overlay>
    </div>
  </Teleport>
</template>

<style scoped lang="scss">
.PopupOverlay {
  &:not(.page) {
    .Overlay {
      position: absolute;
    }
  }
}
</style>
