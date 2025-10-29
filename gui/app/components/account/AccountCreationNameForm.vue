<script setup lang="ts">
const name = defineModel<string>('name', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next'])

const next = () => unref(valid) && emit('next')
</script>

<template>
  <section class="AccountCreationNameForm">
    <AccountNameInput
      v-model:name="name"
      v-model:valid="valid"
      msg-placement="top"
      :tabindex="0"
      autofocus
      @next="() => emit('next')"
    />
    <TextButton
      aspect="flat"
      size="large"
      color="primary"
      :disabled="!valid"
      @click="next"
    >
      Continuer
    </TextButton>
  </section>
</template>

<style scoped lang="scss">
.AccountCreationNameForm {
  @include flex-column;
  align-items: stretch;
  gap: 1em;
}
</style>
