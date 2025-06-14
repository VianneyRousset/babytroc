<script setup lang="ts">
const props = defineProps<{
  modelValue: string
}>()
const emit = defineEmits<(event: 'update:modelValue', modelValue: string) => void>()

const name = ref<string>(unref(props.modelValue))

const touched = ref(false)
const { name: cleanedName, status, error } = useUserNameValidity(name, useThrottle(touched, 1000).value)

watch(() => props.modelValue, (_model) => {
  name.value = _model
})

watch(cleanedName, _name => emit('update:modelValue', _name))

watchEffect(() => {
  if (unref(name).length > 0)
    touched.value = true
})
</script>

<template>
  <div class="MeAccountName">
    <TextInput
      v-model="name"
      type="text"
      placeholder="Pseudonyme"
      msg-placement="top"
      autofocus
      :tabindex="1"
      :status="status"
      :msg-error="error"
      @blur="touched = true"
    />
    <TextButton
      aspect="flat"
      size="large"
      color="primary"
      tabindex="2"
      :disabled="status !== 'success'"
    >
      Continuer
    </TextButton>
  </div>
</template>

<style scoped lang="scss">
.MeAccountName {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;
}
</style>
