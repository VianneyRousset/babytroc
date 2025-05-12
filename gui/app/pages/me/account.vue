<script setup lang="ts">
import { LockKeyhole, LockKeyholeOpen } from 'lucide-vue-next'

const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

const {
  loggedIn,
  loggedInStatus,
  username,
  password,
  login,
  loginStatus,
  loginAsyncStatus,
  logout,
} = useAuth()
const { data: me } = useMeQuery()

const usernameInput = useTemplateRef('usernameInput')
const passwordInput = useTemplateRef('passwordInput')

const route = useRoute()

watch(loggedIn, (newState, oldState) => {
  if (oldState === false && newState === true && route.query.redirect)
    navigateTo(route.query.redirect as string)
})

const enableLogin = computed<boolean>(() => unref(username).length > 0 && unref(password).length > 0)
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="main-header">
      <AppBack />
      <h1>Compte</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <!-- Loader when not knowing if logged in -->
      <div
        v-if="loggedInStatus === 'pending'"
        class="app-content flex-column-center"
      >
        <LoadingAnimation />
      </div>

      <!-- Not logged in: show login form -->
      <div
        v-else-if="loggedIn === false"
        class="app-content page"
      >
        <div
          class="lock"
          :class="{ red: loginStatus === 'error' }"
        >
          <div>
            <LockKeyholeOpen
              :size="48"
              :stroke-width="2"
            />
          </div>
          <div v-if="loginStatus !== 'error'">
            Vous n'êtes pas connecté
          </div>
          <div v-else>
            Email ou mot de passe invalide
          </div>
        </div>
        <h2>Se connecter</h2>
        <div class="form">
          <input
            ref="usernameInput"
            v-model="username"
            type="email"
            placeholder="Email"
            tabindex="1"
            autofocus
            @keyup.enter="passwordInput?.focus()"
          >
          <input
            ref="passwordInput"
            v-model="password"
            type="password"
            placeholder="Password"
            tabindex="2"
            @keyup.enter="login"
          >
          <TextButton
            aspect="flat"
            size="large"
            color="primary"
            :loading="loginAsyncStatus === 'loading'"
            tabindex="3"
            :disabled="!enableLogin"
            @click="enableLogin ? login() : null"
          >
            Valider
          </TextButton>
        </div>
      </div>

      <div
        v-else-if="loggedIn === true"
        class="app-content page"
      >
        <div class="lock">
          <div>
            <LockKeyhole
              :size="48"
              :stroke-width="2"
            />
          </div>
          <div>{{ me?.email }}</div>
        </div>
        <TextButton
          aspect="bezel"
          size="large"
          @click="logout"
        >
          Se déconnecter
        </TextButton>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}

.lock {
  @include flex-column-center;
  gap: 1rem;
  height: 8rem;
  width: 100%;
  color: $neutral-800;

  &.red {
    color: $red-800;
  }
}

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
</style>
