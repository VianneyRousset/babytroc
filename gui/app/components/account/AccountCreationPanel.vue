<script setup lang="ts">
const { goBack } = useNavigation()


// const { mutateAsync: submit, asyncStatus: submitAsyncStatus } = useCreateAccountMutation()

/*
async function create() {
  if (!unref(isValid))
    return

  await submit({
    name: unref(name),
    email: unref(email),
    password: unref(password),
  })
  navigateTo('/me/account/pending-validation')
}

const email = ref('')

}
*/
</script>

<template>
  <Panel class="AccountCreationPanel">
    <transition
      name="slide-right-left"
      mode="in-out"
      appear
    >
    </transition>
  </Panel>
              <!-- Continuer -->
            <!-- </TextButton> -->
          <!-- </div> -->
          <!-- password input -->
          <!-- <div -->
            <!-- v-else-if="mode === 'password'" -->
            <!-- class="vbox" -->
          <!-- > -->
            <!-- <PageDecoration> -->
              <!-- <KeyRound -->
                <!-- :size="64" -->
                <!-- :stroke-width="1.33" -->
              <!-- /> -->
            <!-- </PageDecoration> -->
            <!-- <AccountPasswordInput -->
              <!-- v-model="password" -->
              <!-- msg-placement="top" -->
              <!-- @update:status="_status => (passwordStatus = _status)" -->
              <!-- @enter="create" -->
            <!-- /> -->
            <!-- <TextButton -->
              <!-- aspect="bezel" -->
              <!-- size="large" -->
              <!-- color="primary" -->
              <!-- :disabled="!isValid" -->
              <!-- :loading="submitAsyncStatus === 'loading'" -->
              <!-- :timeout="0" -->
              <!-- @click="create" -->
            <!-- > -->
              <!-- Enregistrer -->
            <!-- </TextButton> -->
          <!-- </div> -->
        <!-- </transition> -->
  
    <!-- Banner -->
    <!-- <transition -->
      <!-- name="pop" -->
      <!-- mode="out-in" -->
      <!-- appear -->
    <!-- > -->
      <!-- Success -->
      <!-- <PanelBanner -->
        <!-- v-if="status === 'success'" -->
        <!-- color="primary" -->
        <!-- :icon="Check" -->
      <!-- > -->
        <!-- Demande envoyée. Un email vous a été envoyé. -->
      <!-- </PanelBanner> -->

      <!-- Error -->
      <!-- <PanelBanner -->
        <!-- v-else-if="status === 'error'" -->
        <!-- color="red" -->
        <!-- :icon="OctagonAlert" -->
      <!-- > -->
        <!-- Une erreur est survenue -->
      <!-- </PanelBanner> -->

      <!-- Idle -->
      <!-- <PanelBanner -->
        <!-- v-else -->
        <!-- :icon="UserRoundPlus" -->
      <!-- /> -->
    <!-- </transition> -->

    <!-- Form -->
    <!-- <h2>Vous avez oublié votre mot de passe?</h2> -->
    <!-- <p>Pas de soucis, on ne vous en veut pas. Entrez ici votre adresse email et nous vous enverrons un courriel pour le réinitialiser.</p> -->
    <!-- <WithDropdownMessage -->
      <!-- :status="validationStatus" -->
      <!-- :msg-error="validationError" -->
      <!-- msg-placement="top" -->
    <!-- > -->
      <!-- <TextInput -->
        <!-- v-model="email" -->
        <!-- type="email" -->
        <!-- placeholder="Email" -->
        <!-- :tabindex="1" -->
        <!-- autofocus -->
        <!-- :status="validationStatus" -->
        <!-- :disabled="isLoading || status === 'success'" -->
        <!-- @keyup.enter="go" -->
      <!-- /> -->
    <!-- </WithdropdownMessage> -->
    <!-- <TextButton -->
      <!-- aspect="bezel" -->
      <!-- size="large" -->
      <!-- color="neutral" -->
      <!-- :loading="isLoading" -->
      <!-- :disabled="validationStatus !== 'success' || status === 'success'" -->
      <!-- @click="go" -->
    <!-- > -->
      <!-- Réinitialiser -->
    <!-- </TextButton> -->
  <!-- </Panel> -->
</template>

<style scoped lang="scss">
.AccountAskPasswordResetPanel {
}
</style>
