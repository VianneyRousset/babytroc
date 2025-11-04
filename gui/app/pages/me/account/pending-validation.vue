<script setup lang="ts">
import { Check, OctagonAlert, X } from 'lucide-vue-next'

definePageMeta({
  layout: 'me-account-pending-validation',
})

const {
  mutateAsync: resendValidationEmail,
  asyncStatus: resendValidationEmailAsyncStatus,
} = useResendValidationEmailMutation()

const error = ref<boolean>(false)
const { loggedIn } = useAuth()
const { $api } = useNuxtApp()

watch(loggedIn, (state) => {
  if (state !== true)
    return

  setTimeout(() => navigateTo('/me/account'), 1200)
})

// resend validation email if specified
const route = useRoute()
const router = useRouter()
if (route.query.sendEmail !== undefined) {
  resendValidationEmail()
  router.replace({ query: {} })
}

const queryCache = useQueryCache()
useLiveMessage('updated_account_validation', () => {
  $api('/v1/auth/refresh', { method: 'POST' })
    .then(() => queryCache.invalidateQueries({ key: ['auth'] }))
})
</script>

<template>
  <AppPage
    :max-width="800"
  >
    <!-- Header (desktop only) -->
    <NuxtLink
      to="/me/account"
    >
      <X
        style="cursor: pointer; margin: 1em;"
        :size="32"
        :stroke-width="2"
      />
    </NuxtLink>

    <!-- Main content -->
    <main>
      <transition
        name="pop"
        mode="out-in"
        appear
      >
        <!-- Validated -->
        <Panel v-if="loggedIn === true">
          <PanelBanner
            :icon="Check"
            color="primary"
          >
            <h2>Votre compte a été validé</h2>
          </PanelBanner>
        </Panel>

        <!-- Erreur -->
        <Panel v-else-if="error">
          <PanelBanner
            :icon="OctagonAlert"
            color="red"
          >
            <h2>Une erreur est survenue.</h2>
          </PanelBanner>
        </Panel>

        <!-- Pending validation -->
        <Panel
          v-else
          class="pending"
        >
          <PanelBanner>
            <LoadingAnimation />
            <h1>En attente de validation...</h1>
            <div>Un email de validation vous été envoyé.</div>
            <TextButton
              aspect="outline"
              color="neutral"
              :loading="resendValidationEmailAsyncStatus === 'loading'"
              :timeout="0"
              @click="resendValidationEmail"
            >
              Renvoyer un email
            </TextButton>
          </PanelBanner>
        </Panel>
      </transition>
    </main>
  </AppPAge>
</template>

<style scoped lang="scss">
.AppPage {
  min-height: 0;
  align-items: stretch;

  a {
    @include reset-link;
  }

  .Panel {

    .LoadingAnimation {
      margin: 4em 0;
    }

    h1 {
      margin: 1em 0;
    }

    .TextButton {
      margin-top: 1em;
    }
  }
}
</style>
