<script setup lang="ts">
const props = defineProps<{
  modelValue: AgeRange
}>()
const emit = defineEmits<
  (e: 'update:modelValue', value: AgeRange) => void
>()

const rangeMin = 0
const rangeMax = 24
const range = ref<[number, number]>([
  props.modelValue[0] ?? rangeMin,
  props.modelValue[1] ?? rangeMax,
])

watch(
  () => props.modelValue,
  (value) => {
    range.value = [value[0] ?? rangeMin, value[1] ?? rangeMax]
  },
)

function onChange(value: number[] | undefined) {
  if (value === undefined)
    return

  const lower = value[0]
  const upper = value[1]

  if (lower === undefined || upper === undefined) return

  emit('update:modelValue', [
    lower,
    upper === rangeMax ? null : upper,
  ])
}

function formatMonth(month: number): string {
  if (month === rangeMax) return `${rangeMax}+ mois`

  return `${month} mois`
}

const displayedMin = computed(() => formatMonth(range.value[0]))
const displayedMax = computed(() => formatMonth(range.value[1]))
</script>

<template>
  <div class="AgeRangeInput">
    <SliderRoot
      :model-value="range"
      class="SliderRoot"
      :min="rangeMin"
      :max="rangeMax"
      :step="1"
      @update:model-value="onChange"
    >
      <SliderTrack class="SliderTrack">
        <SliderRange class="SliderRange" />
      </SliderTrack>
      <SliderThumb class="SliderThumb">
        <div>{{ displayedMin }}</div>
      </SliderThumb>
      <SliderThumb class="SliderThumb">
        <div>{{ displayedMax }}</div>
      </SliderThumb>
    </SliderRoot>
  </div>
</template>

<style scoped lang="scss">
.AgeRangeInput {

  @include flex-column;
  align-items: stretch;
  gap: 0.5em;
  padding: 0em 1em;
  padding-top: 2.5em;

  .SliderTrack {
    border-radius: 1em;
    height: round(up, 0.3em, 1px);

    .SliderRange {
      border-radius: 1em;
    }
  }

  .SliderThumb {

    width: round(up, 1.5em, 1px);
    height: round(up, 1.5em, 1px);

    div {

    position: relative;
    top: -3em;

    font-size: round(up, 0.7em, 1px);
    white-space: nowrap;
    color: white;
    box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
    background: $primary-400;
    border-radius: 8px;
    padding: 0.3em 0.6em;
    }
  }
}
</style>
