<script setup lang="ts">
import {
	ArrowLeft,
	AtSign,
	Check,
	KeyRound,
	OctagonAlert,
	UserRoundPlus,
} from "lucide-vue-next";
import type { FetchError } from "ofetch";

definePageMeta({
	layout: "me",
	appBack: "/me/account",
});

const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;

const name = ref("");
const email = ref("");
const password = ref("");
const capToken = ref("");
const website = ref("");
const passwordFormRef = useTemplateRef("passwordFormRef");

const modeCounter = ref(0);
const mode = computed(() => {
	return {
		0: "name",
		1: "email",
		2: "password",
	}[unref(status) === "success" ? 2 : unref(modeCounter)];
});

// account creation
const { createAccount, isLoading, status } = useCreateAccount({
	onSuccess: () =>
		setTimeout(() => navigateTo("/me/account/pending-validation"), 1200),
});

const { goBack } = useNavigation();

// when the account creation request is pending or succeeded
// it is impossible to go back or resend a request
const freeze = computed(() => unref(isLoading) || unref(status) === "success");

function mapErrorToToast(err: FetchError | null): void {
	const code = err?.status;
	if (code === 400) {
		$toast.error("Captcha invalide, veuillez réessayer.");
	} else if (code === 422) {
		$toast.error("Champs invalides.");
	} else if (code === 429) {
		$toast.error("Trop d'envois. Réessayez dans quelques minutes.");
	} else if (typeof code === "number" && code >= 500) {
		$toast.error("Erreur serveur. Réessayez plus tard.");
	} else {
		$toast.error("Problème de connexion. Vérifiez votre réseau.");
	}
}

async function next() {
	const _modeCounter = unref(modeCounter);

	if (unref(freeze)) return;

	if (_modeCounter === 2) {
		try {
			return await createAccount({
				name: unref(name),
				email: unref(email),
				password: unref(password),
				cap_token: unref(capToken),
				website: unref(website),
			});
		} catch (err) {
			mapErrorToToast(err as FetchError);
			passwordFormRef.value?.bumpResetSignal();
			return;
		}
	}

	modeCounter.value = _modeCounter + 1;
}

function previous() {
	const _modeCounter = unref(modeCounter);

	if (unref(freeze)) return;

	if (_modeCounter === 0) return goBack("/me/account");

	modeCounter.value = _modeCounter - 1;
}
</script>

<template>
  <AppPage
    with-header
    :max-width="600"
  >
    <!-- Header bar (mobile only ) -->
    <template #mobile-header-bar>
      <IconButton :disabled="freeze">
        <ArrowLeft
          style="cursor: pointer;"
          :size="32"
          :stroke-width="2"
          @click="previous"
        />
      </IconButton>
      <h1>Créer un compte</h1>
    </template>

    <!-- Header (desktop only) -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <IconButton :disabled="freeze">
            <ArrowLeft
              style="cursor: pointer;"
              :size="32"
              :stroke-width="2"
              @click="previous"
            />
          </IconButton>
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
            <h2>Entrez votre pseudonyme</h2>
          </PanelBanner>
          <AccountCreationNameForm
            v-model:name="name"
            @next="next"
          />
        </Panel>
        <!-- Email -->
        <Panel v-else-if="mode === 'email'">
          <PanelBanner :icon="AtSign">
            <h2>Entrez votre address email</h2>
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
              <h2>Compte créé avec succés</h2>
            </PanelBanner>
            <PanelBanner
              v-else-if="status === 'error'"
              :icon="OctagonAlert"
            >
              <h2>Une erreur est survenue</h2>
            </PanelBanner>
            <PanelBanner
              v-else
              :icon="KeyRound"
            >
              <h2>Entrer un mot de passe pour votre compte</h2>
            </PanelBanner>
          </transition>
          <AccountCreationPasswordForm
            ref="passwordFormRef"
            v-model:password="password"
            v-model:cap-token="capToken"
            v-model:website="website"
            :loading="isLoading"
            :disabled="freeze"
            :api-url="cap.apiUrl"
            :site-key="cap.siteKey"
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
