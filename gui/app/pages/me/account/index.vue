<script setup lang="ts">
import { Check, OctagonAlert, LockKeyhole, LockKeyholeOpen } from 'lucide-vue-next'

const router = useRouter()

const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

const {
  loggedIn,
  loggedInStatus,
  username,
  password,
  login: _login,
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

async function login() {
  const credentials_info = await _login()
  if (credentials_info.validated === false) {
    navigateTo(router.resolve({
      name: 'me-account-pending-validation',
      query: {
        sendEmail: null,
      },
    }))
  }
}
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
        <PageDecoration>
          <transition
            name="pop"
            mode="out-in"
            appear
          >
            <div
              v-if="loginStatus === 'success'"
              class="success"
            >
              <Check
                :size="64"
                :stroke-width="1.33"
              />
            </div>
            <div
              v-else-if="loginStatus === 'error'"
              class="error"
            >
              <OctagonAlert
                :size="64"
                :stroke-width="1.33"
              />
              <div>Email ou mot de passe invalid</div>
            </div>
            <LockKeyholeOpen
              v-else
              :size="64"
              :stroke-width="1.33"
            />
          </transition>
        </PageDecoration>
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
        <NuxtLink
          class="reset"
          to="/me/account/reset-password"
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
      </div>

      <div
        v-else-if="loggedIn === true"
        class="app-content page"
      >
        <PageDecoration>
          <LockKeyhole
            :size="48"
            :stroke-width="2"
          />
          <div>{{ me?.email }}</div>
        </PageDecoration>
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

a.reset {
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

.success {
  @include flex-column;
  gap: 1rem;
  color: $primary-400;
}

.error {
  @include flex-column;
  gap: 1rem;
  color: $red-800;
}
</style>
