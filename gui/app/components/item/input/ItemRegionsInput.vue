<script setup lang="ts">
const props = defineProps<{
  msgPlacement?: MsgPlacement
  columns?: number
}>()

const { msgPlacement, columns } = toRefs(props)

const regions = defineModel<Set<number>>('regions', { default: new Set<number>() })
const valid = defineModel<boolean>('valid', { default: false })
const touched = defineModel<boolean>('touched', { default: false })

const { status, error } = useItemRegionsValidity(regions, touched)

const stop = watchEffect(() => {
  valid.value = unref(status) === 'success'
})

tryOnUnmounted(stop)
</script>

<template>
  <div
    class="ItemRegionsInput"
    :class="{ error: status === 'error' }"
  >
    <WithDropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <RegionsMap
        v-model="regions"
        editable
      />
      <RegionsList
        v-model="regions"
        :columns="columns"
        editable
      />
    </WithDropdownMessage>
  </div>
</template>

<style lang="scss" scoped>
.ItemRegionsInput {
  .RegionsMap {
    margin: 3em 0;
    transition: filter 200ms ease-out;
  }

  &.error {
    .RegionsMap {
      filter: drop-shadow(0 0 2px $red-800);
    }
  }
}
</style>
