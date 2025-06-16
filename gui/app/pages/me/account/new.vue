<script setup lang="ts">
import { UserRound, AtSign, KeyRound } from 'lucide-vue-next'
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

const name = ref('')
const nameStatus = ref<AsyncStatus>('idle')

const email = ref('')
const emailStatus = ref<AsyncStatus>('idle')

const password = ref('')
const passwordStatus = ref<AsyncStatus>('idle')

const mode = ref<'name' | 'email' | 'password'>('name')

function next() {
  const _mode = unref(mode)

  if (_mode === 'name' && unref(nameStatus) === 'success')
    mode.value = 'email'

  else if (_mode === 'email' && unref(emailStatus) === 'success')
    mode.value = 'password'
}

const { mutateAsync: submit, asyncStatus: submitAsyncStatus } = useCreateAccountMutation()

async function create() {
  await submit({
    name: unref(name),
    email: unref(email),
    password: unref(password),
  })
  navigateTo('/me/account/pending-validation')
}
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="main-header">
      <AppBack />
      <h1>Créer un compte</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <!-- Not logged in: show login form -->
      <div class="app-content page">
        <transition
          name="slide-right-left"
          mode="out-in"
          appear
        >
          <!-- name input -->
          <div
            v-if="mode === 'name'"
            class="vbox"
          >
            <PageDecoration>
              <UserRound
                :size="64"
                :stroke-width="1.33"
              />
            </PageDecoration>
            <AccountNameInput
              v-model="name"
              msg-placement="top"
              @update:status="_status => (nameStatus = _status)"
              @enter="next"
            />
            <TextButton
              aspect="flat"
              size="large"
              color="primary"
              :disabled="nameStatus !== 'success'"
              @click="next"
            >
              Continuer
            </TextButton>
          </div>
          <!-- email input -->
          <div
            v-else-if="mode === 'email'"
            class="vbox"
          >
            <PageDecoration>
              <AtSign
                :size="64"
                :stroke-width="1.33"
              />
            </PageDecoration>
            <AccountEmailInput
              v-model="email"
              msg-placement="top"
              @update:status="_status => (emailStatus = _status)"
              @enter="next"
            />
            <TextButton
              aspect="flat"
              size="large"
              color="primary"
              :disabled="emailStatus !== 'success'"
              @click="next"
            >
              Continuer
            </TextButton>
          </div>
          <!-- password input -->
          <div
            v-else-if="mode === 'password'"
            class="vbox"
          >
            <PageDecoration>
              <KeyRound
                :size="64"
                :stroke-width="1.33"
              />
            </PageDecoration>
            <AccountPasswordInput
              v-model="password"
              msg-placement="top"
              @update:status="_status => (passwordStatus = _status)"
              @enter="create"
            />
            <TextButton
              aspect="bezel"
              size="large"
              color="primary"
              :disabled="passwordStatus !== 'success'"
              :loading="submitAsyncStatus === 'loading'"
              :timeout="0"
              @click="create"
            >
              Enregistrer
            </TextButton>
          </div>
        </transition>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}

.vbox {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;
}
</style>
