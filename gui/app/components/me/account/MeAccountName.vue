<script setup lang="ts">
const model = defineModel<string>({ required: true })
const emit = defineEmits(['next'])

const consecutiveWhitespacesRegex = /[ ]{2,}/g

const name = computed({
  get: () => unref(model),
  set: (v) => {
    model.value = v.trim().replace(consecutiveWhitespacesRegex, ' ')
  },
})

const { value: throttledName, synced: throttledNameSynced } = useThrottle(name, 500)

const {
  data: nameAvailability,
  asyncStatus: nameAvailabilityStatus,
} = useAuthAccountNameAvailable(throttledName)

const touched = ref(false)
const { value: showMsg, synced: showMsgSynced } = useThrottle(touched, 2000)
const isNameAvailable = computed<boolean | undefined>(() => unref(nameAvailability)?.available)
const validCharactersRegex = /^(?![_.-])(?!.*[_.]{2})[a-zA-Z0-9._ -]+(?<![_.-])$/

watchEffect(() => {
  if (unref(name).length > 0)
    touched.value = true
})

const error = computed<string | false>(() => {
  const _name = unref(name)

  if (_name === '')
    return 'Veuillez spécifier un pseudonyme'

  if (_name.length < 3)
    return 'Pseudonyme trop court'

  if (_name.length > 30)
    return 'Pseudonyme trop long'

  if (unref(nameAvailability)?.available === false)
    return 'Pseudonyme est déjà utilisé'

  if (!validCharactersRegex.test(unref(name)))
    return 'Pseudonymeom invalid'

  return false
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
      :loading="!showMsgSynced || !throttledNameSynced || nameAvailabilityStatus === 'loading'"
      :error="showMsg && error"
      :success="touched"
      @blur="touched = true"
    />
    <TextButton
      aspect="flat"
      size="large"
      color="primary"
      tabindex="2"
      :disabled="isNameAvailable === false || !showMsgSynced || !throttledNameSynced"
      @click="emit('next')"
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
