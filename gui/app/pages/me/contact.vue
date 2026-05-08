<script setup lang="ts">
import { Send } from 'lucide-vue-next'

definePageMeta({
  layout: 'me',
  appBack: true,
  appTitle: 'Contact',
})

const nom = ref('')
const email = ref('')
const sujet = ref('')
const message = ref('')
const sent = ref(false)

function submit() {
  if (!nom.value || !email.value || !sujet.value || !message.value) return
  if (!email.value.includes('@')) return

  sent.value = true
  nom.value = ''
  email.value = ''
  sujet.value = ''
  message.value = ''
}
</script>

<template>
  <AppPage :max-width="600">
    <Panel>
      <section class="intro">
        <p>
          Une question, un problème ou une suggestion&nbsp;? Contactez-nous&nbsp;!
        </p>
        <p>
          Email&nbsp;: <a href="mailto:contact@babytroc.ch">contact@babytroc.ch</a>
        </p>
      </section>

      <section class="form">
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
    </Panel>
  </AppPage>
</template>

<style scoped lang="scss">
.intro {
  @include flex-column;
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
  gap: $space-4;

  h2 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0;
  }

  form {
    @include flex-column;
    gap: $space-4;
  }

  label {
    @include flex-column;
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
