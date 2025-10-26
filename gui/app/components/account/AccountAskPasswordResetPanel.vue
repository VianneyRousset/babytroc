<script setup lang="ts">
import { Check, OctagonAlert, KeyRound } from 'lucide-vue-next'

const emit = defineEmits(['done'])

const email = ref('')

const { askPasswordReset, isLoading, status, validationStatus, validationError } = useAskPasswordReset(email)

async function go() {
  if (unref(validationStatus) !== 'success')
    return

  await askPasswordReset()
  emit('done')
}
</script>

<template>
  <Panel class="AccountAskPasswordReset">
    <!-- Banner -->
    <transition
      name="pop"
      mode="out-in"
      appear
    >
      <!-- Success -->
      <PanelBanner
        v-if="status === 'success'"
        color="primary"
        :icon="Check"
      >
        Demande envoyée. Un email vous a été envoyé.
      </PanelBanner>

      <!-- Error -->
      <PanelBanner
        v-else-if="status === 'error'"
        color="red"
        :icon="OctagonAlert"
      >
        Une erreur est survenue
      </PanelBanner>

      <!-- Idle (logged out) -->
      <PanelBanner
        v-else
        :icon="KeyRound"
      />
    </transition>

    <!-- Form -->
    <h2>Vous avez oublié votre mot de passe?</h2>
    <p>Pas de soucis, on ne vous en veut pas. Entrez ici votre adresse email et nous vous enverrons un courriel pour le réinitialiser.</p>
    <WithDropdownMessage
      :status="validationStatus"
      :msg-error="validationError"
      msg-placement="top"
    >
      <TextInput
        v-model="email"
        type="email"
        placeholder="Email"
        :tabindex="1"
        autofocus
        :status="validationStatus"
        :disabled="isLoading || status === 'success'"
        @keyup.enter="go"
      />
    </WithdropdownMessage>
    <TextButton
      aspect="bezel"
      size="large"
      color="neutral"
      :loading="isLoading"
      :disabled="validationStatus !== 'success' || status === 'success'"
      @click="go"
    >
      Réinitialiser
    </TextButton>
  </Panel>
</template>

<style scoped lang="scss">
.AccountAskPasswordResetPanel {
}
</style>
