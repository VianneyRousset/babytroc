<script setup lang="ts">
import type { AsyncDataRequestStatus as AsyncStatus } from "#app";

definePageMeta({
	layout: "me",
	appBack: true,
	appTitle: "Réinitialiser le mot de passe",
});

const {
	mutateAsync: resetPassword,
	status: resetPasswordStatus,
	asyncStatus: resetPasswordAsyncStatus,
} = useResetPasswordMutation();

const route = useRoute();

const password = ref("");
const passwordStatus = ref<AsyncStatus>("idle");

async function _reset() {
	if (unref(passwordStatus) !== "success") return;

	const code = Array.isArray(route.query.code)
		? (route.query.code[0] ?? "")
		: (route.query.code ?? "");

	await resetPassword({
		authorizationCode: code,
		newPassword: unref(password),
	});
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
          v-if="resetPasswordStatus === 'success'"
          class="success"
        >
          <Check
            :size="64"
            :stroke-width="1.33"
          />
        </div>
        <div
          v-else-if="resetPasswordStatus === 'error'"
          class="error"
        >
          <OctagonAlert
            :size="64"
            :stroke-width="1.33"
          />
          <div>Code de confirmation invalide</div>
        </div>
        <div
          v-else
          class="info"
        >
          <KeyRound
            :size="64"
            :stroke-width="1.33"
          />
          <h1>Réinitialiser votre mot de passe</h1>
        </div>
      </transition>
      <transition
        name="pop"
        mode="out-in"
      >
        <div
          v-if="resetPasswordStatus === 'pending'"
          class="vbox"
        >
          <TextButton
            aspect="flat"
            size="large"
            color="neutral"
            :disabled="passwordStatus !== 'success'"
            :loading="resetPasswordAsyncStatus === 'loading'"
            :timeout="0"
            @click="reset"
          >
            Confirmer
          </TextButton>
        </div>
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
    font-size: 1.75rem;
    font-weight: 700;
  }

  .TextButton {
    margin: 1rem;
  }

  .info {
    @include flex-column;
  }

  .success {
    color: $primary-400;
  }

  .error {
    @include flex-column;
    gap: 1rem;
    color: $red-800;
  }

  .vbox {
    @include flex-column;
    align-items: stretch;
    margin-top: 1rem;

    .AccountPasswordInput {
      min-width: 300px;
      margin: 0 1rem;
    }
  }

}
</style>
