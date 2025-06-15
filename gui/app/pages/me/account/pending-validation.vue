<script setup lang="ts">
import { Check, OctagonAlert, X } from 'lucide-vue-next'

const {
  mutateAsync: resendValidationEmail,
  asyncStatus: resendValidationEmailAsyncStatus,
} = useResendValidationEmailMutation()

const error = ref<boolean>(false)
const { loggedIn } = useAuth()
const routeStack = useRouteStack()
const { data: me } = useMeQuery()

watch(loggedIn, (state) => {
  if (state !== true)
    return

  const _me = unref(me)

  setTimeout(() => {
    routeStack.reset()
    return navigateTo('/')
  }, 750)
})

try {
  const queryCache = useQueryCache()

  // websocket uri
  const loc = window.location
  const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:'
  const uri = `${proto}//${loc.host}/api/v1/me/websocket`

  // open websocket and attach event listener
  const websocket = new WebSocket(uri)

  websocket.addEventListener('message', (event) => {
    try {
      const wsMessage = JSON.parse(event.data)

      if (wsMessage.type === 'updated_account_validation')
        queryCache.invalidateQueries({ key: ['auth'] })
    }
    catch (err) {
      error.value = true
      console.error(err)
    }
  })
}
catch (err) {
  error.value = true
  throw err
}
</script>

<template>
  <div>
    <!-- Main content -->
    <main class="page">
      <NuxtLink
        class="cancel"
        to="/me/account"
      >
        <X
          :size="24"
          :stroke-width="1.33"
        />
        <div>Annuler</div>
      </NuxtLink>
      <transition
        name="pop"
        mode="out-in"
        appear
      >
        <div
          v-if="loggedIn"
          class="success"
        >
          <Check
            :size="64"
            :stroke-width="1.33"
          />
        </div>
        <div
          v-else-if="error"
          class="error"
        >
          <OctagonAlert
            :size="64"
            :stroke-width="1.33"
          />
          <div>Une erreur est survenue.</div>
        </div>
        <LoadingAnimation v-else />
      </transition>
      <h1>En attente de validation...</h1>
      <div>Un email de confirmation vous été envoyé.</div>
      <TextButton
        aspect="outline"
        color="neutral"
        :loading="resendValidationEmailAsyncStatus === 'loading'"
        :timeout="0"
        @click="resendValidationEmail"
      >
        Renvoyer un email
      </TextButton>
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  @include flex-column-center;
  box-sizing: border-box;
  height: 100dvh;
  color: $neutral-600;
  position: relative;

  h1 {
    font-family: "Plus Jakarta Sans", sans-serif;
    text-align: center;
    color: $neutral-800;
    font-size: 1.4rem;
    font-weight: 700;
  }

  .TextButton {
    margin: 1rem;
  }

  a.cancel {
    @include reset-link;
    @include flex-row;
    gap: 0.5rem;
    position: absolute;
    top: 1rem;
    left: 1rem;
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
