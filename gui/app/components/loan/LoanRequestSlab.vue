<script setup lang="ts">
import { Clock, CheckCircle, XCircle } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const props = withDefaults(defineProps<{
  loanRequest: LoanRequest
  target?: string | RouteLocationGeneric
  chevron?: boolean
}>(), {
  chevron: false,
})

const { loanRequest } = toRefs(props)

const { firstImagePath: itemImage } = useItemFirstImage(() => unref(loanRequest).item)

const stateLabel = computed(() => {
  switch (unref(loanRequest).state) {
    case 1: return 'En attente'
    case 3: return 'Acceptée'
    default: return ''
  }
})

const stateIcon = computed(() => {
  switch (unref(loanRequest).state) {
    case 1: return Clock
    case 3: return CheckCircle
    default: return XCircle
  }
})
</script>

<template>
  <Slab
    :target="target"
    :chevron="chevron"
    :icon="stateIcon"
  >
    {{ loanRequest.item.name }}

    <template #sub>
      {{ stateLabel }}
    </template>
  </Slab>
</template>
