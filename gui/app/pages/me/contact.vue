<script setup lang="ts">
definePageMeta({
	layout: "me",
	appBack: true,
	appTitle: "Contact",
});

const nom = ref("");
const email = ref("");
const sujet = ref("");
const message = ref("");
const sent = ref(false);

function _submit() {
	if (!nom.value || !email.value || !sujet.value || !message.value) return;
	if (!email.value.includes("@")) return;

	sent.value = true;
	nom.value = "";
	email.value = "";
	sujet.value = "";
	message.value = "";
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
            v-if="sent"
            class="success"
          >
            <p>Merci&nbsp;! Votre message a bien été envoyé.</p>
            <TextButton
              aspect="outline"
              size="small"
              @click="sent = false"
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
              />
            </label>
            <label>
              Email
              <TextInput
                v-model="email"
                type="email"
                placeholder="Votre adresse email"
              />
            </label>
            <label>
              Sujet
              <TextInput
                v-model="sujet"
                placeholder="Sujet de votre message"
              />
            </label>
            <label>
              Message
              <LongTextInput
                v-model="message"
                placeholder="Votre message..."
              />
            </label>
            <TextButton
              aspect="flat"
              color="primary"
              :icon="Send"
              :disabled="!nom || !email || !sujet || !message"
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
