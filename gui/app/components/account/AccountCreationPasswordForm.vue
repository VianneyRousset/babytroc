<script setup lang="ts">
const props = defineProps<{
  loading?: boolean
  disabled?: boolean
}>()

const { loading, disabled } = toRefs(props)

const password = defineModel<string>('password', { default: '' })
const valid = defineModel<boolean>('valid')
const emit = defineEmits(['next'])

const next = () => unref(valid) && emit('next')
</script>

<template>
  <section class="AccountCreationPasswordForm">
    <AccountPasswordInput
      v-model:password="password"
      v-model:valid="valid"
      msg-placement="top"
      :tabindex="0"
      :disabled="loading || disabled"
      autofocus
      @next="() => emit('next')"
    />
    <TextButton
      aspect="flat"
      size="large"
      color="primary"
      :loading="loading"
      :disabled="!valid || loading || disabled"
      @click="next"
    >
      Créer un compte
    </TextButton>
  </section>
</template>

<style scoped lang="scss">
.AccountCreationPasswordForm {
  @include flex-column;
  align-items: stretch;
  gap: 1em;
}
</style>
