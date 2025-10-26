<script setup lang="ts">
import { Check, OctagonAlert, LockKeyholeOpen } from 'lucide-vue-next'

const { login: _login, isLoading, status } = useLogin()

const username = ref('')
const password = ref('')

// login form validity
const valid = computed<boolean>(() => unref(username).length > 0 && unref(password).length > 0)

const router = useRouter()
async function login() {
  // skip if invalid login form
  if (!unref(valid))
    return

  // login request
  const credentials_info = await _login({
    username: unref(username),
    password: unref(password),
  })

  // navigate to pending account validation page if account is not validated yet
  if (credentials_info.validated === false) {
    navigateTo(router.resolve({
      name: 'me-account-pending-validation',
      query: {
        sendEmail: null,
      },
    }))
  }
}

// input elements
const usernameInput = useTemplateRef<HTMLInputElement>('usernameInput')
const passwordInput = useTemplateRef<HTMLInputElement>('passwordInput')

// empty form inputs if status transitions to error
const stop = watch(status, (newStatus, oldStatus) => {
  if (oldStatus !== 'error' && newStatus === 'error') {
    username.value = ''
    password.value = ''
  }
})

tryOnUnmounted(stop)
</script>

<template>
  <Panel class="AccountLoginPanel">
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
        Vous êtes connecté
      </PanelBanner>

      <!-- Error -->
      <PanelBanner
        v-else-if="status === 'error'"
        color="red"
        :icon="OctagonAlert"
      >
        Email ou mot de passe invalid
      </PanelBanner>

      <!-- Idle (logged out) -->
      <PanelBanner
        v-else
        :icon="LockKeyholeOpen"
      >
        Vous n'êtes pas connecté
      </PanelBanner>
    </transition>

    <!-- Login form -->
    <h2>Se connecter</h2>
    <div class="form">
      <input
        ref="usernameInput"
        v-model="username"
        type="email"
        placeholder="Email"
        tabindex="1"
        autofocus
        :disabled="isLoading"
        @keyup.enter="passwordInput?.focus()"
      >
      <input
        ref="passwordInput"
        v-model="password"
        type="password"
        placeholder="Password"
        tabindex="2"
        :disabled="isLoading"
        @keyup.enter="login"
      >
      <TextButton
        aspect="flat"
        size="large"
        color="primary"
        :loading="isLoading"
        tabindex="3"
        :disabled="!valid || isLoading"
        @click="login"
      >
        Valider
      </TextButton>
    </div>
    <NuxtLink
      class="forgotten-password"
      to="/me/account/forgotten-password"
    >
      Mot de pass oublié
    </NuxtLink>
    <div class="hr-container">
      <hr>
      <div>Ou</div>
      <hr>
    </div>
    <NuxtLink
      to="/me/account/new"
      class="create-account-button"
    >
      Créer un compte
    </NuxtLink>
  </Panel>
</template>

<style scoped lang="scss">
.AccountLoginPanel {
  .form {
    @include flex-column;
    align-items: stretch;
    gap: 1rem;

    input {
      border-radius: 0.5rem;
      padding: 0.6rem 1.5rem;
      font-size: 1.5rem;
    }
  }

  a.forgotten-password {
    @include reset-link;
    font-family: "Plus Jakarta Sans", sans-serif;
    padding-top: 0.3rem;
    text-align: center;
    color: $neutral-300;
  }

  .hr-container {
    @include flex-row;
    gap: 1rem;
    padding:  1rem;
    color: $neutral-400;
    font-family: "Plus Jakarta Sans", sans-serif;
    hr {
      flex: 1;
      border: none;
      border-top: 1px solid $neutral-400;
    }
  }

  .create-account-button {
    @include reset-link;
    text-align: center;
    cursor: pointer;
    font-size: 1.5rem;
    padding: 0.6rem 1.5rem;
    color: $neutral-400;
  }





  
}
</style>
