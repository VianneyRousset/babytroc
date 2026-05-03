<script setup lang="ts">
import { ShieldAlert } from 'lucide-vue-next'

const model = defineModel<boolean>({ default: false })

const props = defineProps<{
  submit: (data: { message: string, context: string }) => Promise<unknown>
  context: string
}>()

const message = ref('')
const status = ref<'idle' | 'loading' | 'success' | 'error'>('idle')

const { $toast } = useNuxtApp()

async function send() {
  if (unref(message).trim().length === 0) return

  status.value = 'loading'
  try {
    await props.submit({
      message: unref(message).trim(),
      context: props.context,
    })
    status.value = 'success'
    $toast.success('Signalement envoyé')
    setTimeout(() => { model.value = false }, 1500)
  }
  catch {
    status.value = 'error'
    $toast.error('Échec de l\'envoi')
  }
}

function onClose() {
  model.value = false
  message.value = ''
  status.value = 'idle'
}
</script>

<template>
  <PopupOverlay
    :model-value="model"
    @update:model-value="v => !v && onClose()"
  >
    <ShieldAlert
      :size="64"
      :stroke-width="1"
    />

    <div class="report-content">
      <h2>Signaler un problème</h2>
      <p class="info">
        Décrivez le problème rencontré. Votre signalement sera examiné par notre équipe.
        L'utilisateur concerné ne sera pas informé de votre signalement.
        <NuxtLink
          to="/me/politics"
          class="link"
        >
          En savoir plus
        </NuxtLink>
      </p>

      <textarea
        v-model="message"
        placeholder="Décrivez le problème..."
        :disabled="status === 'loading' || status === 'success'"
        rows="4"
      />
    </div>

    <template #actions>
      <TextButton
        aspect="flat"
        size="large"
        color="red"
        :loading="status === 'loading'"
        :disabled="message.trim().length === 0 || status === 'success'"
        @click="send"
      >
        <template v-if="status === 'success'">
          Envoyé
        </template>
        <template v-else>
          Envoyer
        </template>
      </TextButton>
      <TextButton
        aspect="outline"
        size="large"
        color="neutral"
        :disabled="status === 'loading'"
        @click="onClose"
      >
        Annuler
      </TextButton>
    </template>
  </PopupOverlay>
</template>

<style scoped lang="scss">
.report-content {
  display: flex;
  flex-direction: column;
  gap: $space-3;
  width: 100%;

  h2 {
    color: $text-primary;
    font-size: 1.1rem;
    text-align: center;
  }

  .info {
    color: $text-secondary;
    font-size: 0.85rem;
    line-height: 1.4;
    text-align: center;
  }

  textarea {
    width: 100%;
    min-height: 100px;
    resize: vertical;
    border: 1px solid $border-default;
    border-radius: $radius-sm;
    padding: $space-3;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    box-sizing: border-box;

    &:focus {
      outline: none;
      border-color: $neutral-400;
    }

    &::placeholder {
      color: $text-tertiary;
    }
  }

  .link {
    color: $primary-text-safe;
    text-decoration: underline;
  }
}
</style>
