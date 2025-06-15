<script setup lang="ts">
import { KeyRound, OctagonAlert, Check } from 'lucide-vue-next'

const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

const email = ref('')
const routeStack = useRouteStack()

const touched = ref(false)
const { email: cleanedEmail, status, error } = useAuthPasswordResetValidation(email, useThrottle(touched, 1000).value)

const {
  mutateAsync: askPasswordReset,
  status: askPasswordResetStatus,
  asyncStatus: askPasswordResetAsyncStatus,
  reset: askPasswordResetReset,
} = useAskPasswordResetMutation()
askPasswordResetReset()

watchEffect(() => {
  if (unref(email).length > 0)
    touched.value = true
})

async function go() {
  if (unref(status) !== 'success')
    return

  await askPasswordReset({ email: unref(cleanedEmail) })
  setTimeout(routeStack.goBack, 1000)
}
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="main-header">
      <AppBack />
      <h1>Réinitialisation mot de passe</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main class="app-content page">
      <PageDecoration>
        <transition
          name="pop"
          mode="out-in"
          appear
        >
          <div
            v-if="askPasswordResetStatus === 'success'"
            class="success"
          >
            <Check
              :size="64"
              :stroke-width="1.33"
            />
          </div>
          <div
            v-else-if="askPasswordResetStatus === 'error'"
            class="error"
          >
            <OctagonAlert
              :size="64"
              :stroke-width="1.33"
            />
            <div>Une erreur est survenue</div>
          </div>
          <KeyRound
            v-else
            :size="64"
            :stroke-width="1.33"
          />
        </transition>
      </PageDecoration>
      <h2>Vous avez oublié votre mot de passe?</h2>
      <p>Pas de soucis, on ne vous en veut pas. Entrez ici votre adresse email et nous vous enverrons un courriel pour le réinitialiser.</p>
      <TextInput
        v-model="email"
        type="email"
        placeholder="Email"
        :tabindex="1"
        autofocus
        :status="status"
        :msg-error="error"
        @blur="touched = true"
        @keyup.enter="go"
      />
      <TextButton
        aspect="bezel"
        size="large"
        color="neutral"
        :loading="askPasswordResetAsyncStatus === 'loading'"
        :disabled="status !== 'success'"
        @click="go"
      >
        Réinitialiser
      </TextButton>
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");

  h2 {
    text-align: center;
    padding: 0 1rem;
    margin: 0;
  }

  p {
    padding: 2rem 0.5rem;
    color: $neutral-400;
    margin: 0;
  }

  .success {
    color: $primary-400;
  }

  .error {
    @include flex-column;
    gap: 1rem;
    color: $red-800;
  }
}
</style>
