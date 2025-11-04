<script setup lang="ts">
import { Check, OctagonAlert, AtSign } from 'lucide-vue-next'

definePageMeta({
  layout: 'empty',
})

const {
  mutateAsync: validateAccount,
  status,
  isLoading,
} = useValidateAccountMutation()

const route = useRoute()

watch(status, state => state === 'success' && setTimeout(closeWindow, 2000))

async function validate() {
  const code = Array.isArray(route.query.code) ? route.query.code[0] ?? '' : route.query.code ?? ''

  await validateAccount({ validation_code: code })
}
</script>

<template>
  <AppPage
    :max-width="600"
  >
    <main>
      <transition
        name="pop"
        mode="out-in"
        appear
      >
        <!-- Success -->
        <Panel v-if="status === 'success'">
          <PanelBanner
            :icon="Check"
            color="primary"
          >
            <h1>Addresse e-mail confirmée</h1>
            <h2>Vous pouvez fermer cette page</h2>
          </PanelBanner>
        </Panel>

        <!-- Error -->
        <Panel v-else-if="status === 'error'">
          <PanelBanner
            :icon="OctagonAlert"
            color="red"
          >
            <h1>Code de confirmation invalide</h1>
            <h2>Vous pouvez fermer cette page</h2>
          </PanelBanner>
        </Panel>

        <!-- Pending -->
        <Panel v-else>
          <PanelBanner :icon="AtSign">
            <h1>Confirmer votre addresse e-mail</h1>
          </PanelBanner>
          <TextButton
            aspect="flat"
            size="large"
            color="neutral"
            :loading="isLoading"
            @click="validate"
          >
            Confirmer
          </TextButton>
        </Panel>
      </transition>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
main {
  padding-top: 4em;
  .PanelBanner {
    text-align: center;
  }
}
</style>
