<script setup lang="ts">
import { OctagonAlert, Send } from "lucide-vue-next";
import type { FetchError } from "ofetch";

definePageMeta({
	layout: "me",
	appBack: true,
	appTitle: "Contact",
});

const { $toast } = useNuxtApp();
const { cap } = useRuntimeConfig().public;

const { loggedIn } = useAuth();
const { me } = useMe();

const nom = ref("");
const email = ref("");
const sujet = ref("");
const message = ref("");
const capToken = ref("");
const website = ref(""); // honeypot
const capResetSignal = ref(0);
const dismissedSuccess = ref(false);

const { sendContactMessage, isLoading, status, error } =
	useSendContactMessage();

// Pre-fill from authenticated session once it resolves
watch(
	[loggedIn, me],
	([loggedInValue, meValue]) => {
		if (loggedInValue !== true || meValue == null) return;
		if (unref(nom) === "") nom.value = meValue.name;
		if (unref(email) === "") email.value = meValue.email;
	},
	{ immediate: true },
);

const capConfigured = computed<boolean>(
	() => cap.apiUrl !== "" && cap.siteKey !== "",
);

const messageTooLong = computed<boolean>(() => unref(message).length > 5000);

const emailValid = computed<boolean>(() =>
	/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(unref(email)),
);

const valid = computed<boolean>(
	() =>
		unref(nom).trim() !== "" &&
		unref(sujet).trim() !== "" &&
		unref(message).trim() !== "" &&
		unref(emailValid) &&
		!unref(messageTooLong) &&
		unref(capToken) !== "" &&
		unref(website) === "" && // honeypot must remain empty
		unref(capConfigured),
);

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

async function submit() {
	if (!unref(valid) || unref(isLoading)) return;

	try {
		await sendContactMessage({
			name: unref(nom),
			email: unref(email),
			subject: unref(sujet),
			message: unref(message),
			capToken: unref(capToken),
		});
		// success — clear editable fields, reset widget (token consumed)
		sujet.value = "";
		message.value = "";
		capToken.value = "";
		capResetSignal.value += 1;
		dismissedSuccess.value = false;
	} catch {
		mapErrorToToast(unref(error));
		capToken.value = "";
		capResetSignal.value += 1;
	}
}

function resetForNewMessage() {
	dismissedSuccess.value = true;
}
</script>

<template>
  <AppPage
    with-header
    :max-width="600"
  >
    <main>
      <section class="section intro">
        <p>
          Une question, un problème ou une suggestion&nbsp;? Contactez-nous&nbsp;!
        </p>
        <p>
          Email&nbsp;: <a href="mailto:contact@babytroc.ch">contact@babytroc.ch</a>
        </p>
      </section>

      <hr class="divider">

      <section class="section form">
        <h2>Formulaire de contact</h2>

        <transition
          name="pop"
          mode="out-in"
        >
          <div
            v-if="status === 'success' && !dismissedSuccess"
            class="success"
          >
            <p>Merci&nbsp;! Votre message a bien été envoyé.</p>
            <TextButton
              aspect="outline"
              size="small"
              @click="resetForNewMessage"
            >
              Envoyer un autre message
            </TextButton>
          </div>

          <form
            v-else
            @submit.prevent="submit"
          >
            <label>
              Nom
              <TextInput
                v-model="nom"
                placeholder="Votre nom"
                :readonly="loggedIn === true"
                :disabled="isLoading"
              />
            </label>
            <label>
              Email
              <TextInput
                v-model="email"
                type="email"
                placeholder="Votre adresse email"
                :readonly="loggedIn === true"
                :disabled="isLoading"
              />
            </label>
            <label>
              Sujet
              <TextInput
                v-model="sujet"
                placeholder="Sujet de votre message"
                :disabled="isLoading"
              />
            </label>
            <label>
              Message
              <LongTextInput
                v-model="message"
                placeholder="Votre message..."
                :disabled="isLoading"
              />
              <small
                class="counter"
                :class="{ over: messageTooLong }"
              >{{ message.length }} / 5000</small>
            </label>

            <Honeypot v-model="website" />

            <CapWidget
              v-if="capConfigured"
              :api-url="cap.apiUrl"
              :site-key="cap.siteKey"
              :reset-signal="capResetSignal"
              :disabled="isLoading"
              @solve="capToken = $event"
              @expire="capToken = ''"
            />
            <PanelBanner
              v-else
              color="red"
              :icon="OctagonAlert"
            >
              Captcha indisponible. Le formulaire est désactivé.
            </PanelBanner>

            <TextButton
              aspect="flat"
              color="primary"
              :icon="Send"
              :disabled="!valid || isLoading"
              :loading="isLoading"
              @click="submit"
            >
              Envoyer
            </TextButton>
          </form>
        </transition>
      </section>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
main {
  @include flex-column;
  gap: 0;
  padding: $space-4;
}

.divider {
  border: none;
  border-top: 1px solid $divider;
  margin: $space-2 0;
}

.section {
  padding: $space-6 0;
}

.intro {
  @include flex-column;
  align-items: stretch;
  gap: $space-2;

  p {
    margin: 0;
    color: $text-secondary;
    line-height: 1.6;
  }

  a {
    color: $primary-600;
    font-weight: 600;
  }
}

.form {
  @include flex-column;
  align-items: stretch;
  gap: $space-4;

  h2 {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin: 0;
  }

  form {
    @include flex-column;
    align-items: stretch;
    gap: $space-4;
  }

  label {
    @include flex-column;
    align-items: stretch;
    gap: $space-1;
    font-size: 0.875rem;
    font-weight: 500;
    color: $text-secondary;
  }

  .counter {
    font-size: 0.75rem;
    color: $text-tertiary;
    align-self: flex-end;

    &.over {
      color: $red-600;
      font-weight: 600;
    }
  }

  .success {
    @include flex-column;
    align-items: center;
    gap: $space-4;
    padding: $space-8 0;
    text-align: center;

    p {
      margin: 0;
      color: $text-primary;
      font-weight: 600;
    }
  }
}
</style>
