<script setup lang="ts">
const email = defineModel<string>('email', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next'])

const next = () => unref(valid) && emit('next')
</script>

<template>
  <section class="AccountCreationEmailForm">
    <AccountEmailInput
      v-model:email="email"
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
.AccountCreationEmailForm {
  @include flex-column;
  align-items: stretch;
  gap: 1em;
}
</style>
