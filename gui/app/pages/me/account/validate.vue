<script setup lang="ts">
import { Check, OctagonAlert, AtSign } from 'lucide-vue-next'

const {
  mutateAsync: validateAccount,
  status: validateAccountStatus,
  asyncStatus: validateAccountAsyncStatus,
} = useValidateAccountMutation()

const route = useRoute()

async function validate() {
  const code = Array.isArray(route.query.code) ? route.query.code[0] ?? '' : route.query.code ?? ''

  await validateAccount({ validation_code: code })
}
</script>

<template>
  <AppPage>
    <!-- Main content -->
    <Panel>
      <transition
        name="pop"
        mode="out-in"
        appear
      >
        <div
          v-if="validateAccountStatus === 'success'"
          class="success"
        >
          <Check
            :size="64"
            :stroke-width="1.33"
          />
        </div>
        <div
          v-else-if="validateAccountStatus === 'error'"
          class="error"
        >
          <OctagonAlert
            :size="64"
            :stroke-width="1.33"
          />
          <div>Code de confirmation invalide</div>
        </div>
        <AtSign
          v-else
          :size="64"
          :stroke-width="1.33"
        />
      </transition>
      <h1>Confirmer votre adresse email</h1>
      <transition
        name="pop"
        mode="out-in"
      >
        <TextButton
          v-if="validateAccountStatus === 'pending'"
          aspect="flat"
          size="large"
          color="neutral"
          :loading="validateAccountAsyncStatus === 'loading'"
          :timeout="0"
          @click="validate"
        >
          Confirmer
        </TextButton>
      </transition>
    </Panel>
  </AppPage>
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
