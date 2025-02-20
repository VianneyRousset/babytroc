<script setup lang="ts">
const props = defineProps<{
  modelValue: Array<number | null>,
}>();
const emit = defineEmits<{
  (e: "update:modelValue", value: Array<number | null>): void
}>();

const rangeMin = 0;
const rangeMax = 24;
const range = ref([props.modelValue[0] ?? rangeMin, props.modelValue[1] ?? rangeMax]);

watch(() => props.modelValue, (value) => {

  range.value = [
    value[0] ?? rangeMin,
    value[1] ?? rangeMax
  ]

});

function onChange(value: number[] | undefined) {

  if (value !== undefined)
    emit('update:modelValue', [
      value[0],
      value[1] === rangeMax ? null : value[1],
    ]);
}

function formatMonth(month: number): string {

  if (month === rangeMax)
    return `${rangeMax}+ mois`;

  return `${month} mois`;
}

const displayedMin = computed(() => formatMonth(range.value[0]));
const displayedMax = computed(() => formatMonth(range.value[1]));

</script>

<template>

  <div class="AgeRangeInput">
    <SliderRoot :modelValue="range" @update:modelValue="onChange" class="SliderRoot" :min="rangeMin" :max="rangeMax"
      :step="1">
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
  gap: 0.5rem;
  padding: 0rem 2rem;
  padding-top: 2.5rem;

  .SliderThumb {
    div {

      position: relative;
      top: -2.5rem;

      font-size: 0.8rem;
      white-space: nowrap;
      color: white;
      box-shadow: 0px 1px 4px rgba(0, 0, 0, 0.2);
      background: $primary-400;
      border-radius: 8px;
      padding: 0.4rem 0.6rem;
    }

  }

}
</style>
