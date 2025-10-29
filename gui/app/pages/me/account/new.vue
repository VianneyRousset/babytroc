<script setup lang="ts">
import { UserRoundPlus, ArrowLeft, AtSign, KeyRound, Check, OctagonAlert } from 'lucide-vue-next'

const name = ref('')
const email = ref('')
const password = ref('')

const modeCounter = ref(0)
const mode = computed(() => {
  return {
    0: 'name',
    1: 'email',
    2: 'password',
  }[unref(modeCounter)]
})

const { createAccount, isLoading, status } = useCreateAccount()

const { goBack } = useNavigation()

async function next() {
  const _modeCounter = unref(modeCounter)

  if (_modeCounter === 2)
    return await createAccount({
      name: unref(name),
      email: unref(email),
      password: unref(password),
    })

  modeCounter.value = _modeCounter + 1
}

function previous() {
  const _modeCounter = unref(modeCounter)

  if (_modeCounter === 0)
    return goBack('/me/account')

  modeCounter.value = _modeCounter - 1
}
</script>

<template>
  <AppPage
    with-header
    :max-width="600"
  >
    <!-- Header bar (mobile only ) -->
    <template #mobile-header-bar>
      <ArrowLeft
        style="cursor: pointer;"
        :size="32"
        :stroke-width="2"
        @click="previous"
      />
      <h1>Réinitialisation mot de passe</h1>
    </template>

    <!-- Header (desktop only) -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <ArrowLeft
            style="cursor: pointer;"
            :size="32"
            :stroke-width="2"
            @click="previous"
          />
        </template>
      </AppHeaderDesktop>
    </template>

    <!-- Main content -->
    <main>
      <transition
        name="fade"
        mode="out-in"
      >
        <!-- Name -->
        <Panel v-if="mode === 'name'">
          <PanelBanner :icon="UserRoundPlus">
            <h2>Entrez un pseudonyme.</h2>
          </PanelBanner>
          <AccountCreationNameForm
            v-model:name="name"
            @next="next"
          />
        </Panel>
        <!-- Email -->
        <Panel v-else-if="mode === 'email'">
          <PanelBanner :icon="AtSign">
            <h2>Entrez votre address email.</h2>
          </PanelBanner>
          <AccountCreationEmailForm
            v-model:email="email"
            @next="next"
          />
        </Panel>
        <!-- Password -->
        <Panel v-else-if="mode === 'password'">
          <transition
            name="pop"
            mode="out-in"
          >
            <PanelBanner
              v-if="status === 'success'"
              :icon="Check"
              color="primary"
            >
              <h2>Compte crée avec succés. Un email de validation vous à été envoyé.</h2>
            </PanelBanner>
            <PanelBanner
              v-else-if="status === 'error'"
              :icon="OctagonAlert"
            >
              <h2>Une erreur est survenue.</h2>
            </PanelBanner>
            <PanelBanner
              v-else
              :icon="KeyRound"
            >
              <h2>Entrer un mot de passe pour votre compte.</h2>
            </PanelBanner>
          </transition>
          <AccountCreationPasswordForm
            v-model:password="password"
            :loading="isLoading"
            @next="next"
          />
        </Panel>
      </transition>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
main {
  position: relative;

  & > .Panel {
    position: absolute;
    width: 100%;
  }
}
</style>
