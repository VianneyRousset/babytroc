# Info Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace placeholder content in 4 info pages (`/me/about`, `/me/faq`, `/me/contact`, `/me/politics`) with real French content.

**Architecture:** Four independent Vue page files already exist as stubs. Each gets its placeholder replaced with final content. No new components, no new dependencies. The contact page adds minor reactive state for form handling.

**Tech Stack:** Vue 3 (Composition API), Nuxt 3, SCSS, existing UI components (`Panel`, `PanelBanner`, `TextInput`, `LongTextInput`, `TextButton`)

---

## File Structure

All files already exist — this is modification only:

| File | Responsibility |
|------|---------------|
| `app/pages/me/about.vue` | Static about page with hero, mission, steps, values |
| `app/pages/me/faq.vue` | FAQ accordion using `<details>/<summary>` |
| `app/pages/me/contact.vue` | Contact form (frontend-only) with email link |
| `app/pages/me/politics.vue` | Static policies: conditions, privacy, community rules |

No test files — these are static content pages with no business logic worth unit-testing. Visual verification via dev server.

---

### Task 1: About page (`/me/about`)

**Files:**
- Modify: `app/pages/me/about.vue`

- [ ] **Step 1: Replace about.vue with final content**

Replace the entire file content with:

```vue
<script setup lang="ts">
definePageMeta({
  layout: 'me',
  appBack: true,
  appTitle: 'A propos',
})
</script>

<template>
  <AppPage :max-width="600">
    <Panel>
      <PanelBanner>
        <h1 class="logo">
          Babytroc
        </h1>
        <p class="tagline">
          La plateforme lausannoise de pr&ecirc;t d'articles pour enfants entre particuliers.
        </p>
      </PanelBanner>

      <section>
        <h2>Notre mission</h2>
        <p>
          Babytroc est n&eacute;e d'une id&eacute;e simple : les enfants grandissent vite,
          mais leurs affaires peuvent encore servir. Notre mission est de r&eacute;duire le
          gaspillage, renforcer la confiance entre parents et rendre la parentalit&eacute;
          plus accessible en facilitant le pr&ecirc;t d'articles pour enfants entre familles.
        </p>
      </section>

      <section>
        <h2>Comment &ccedil;a marche</h2>
        <ol>
          <li>
            <strong>Publiez</strong> vos articles pour enfants que vous n'utilisez plus
          </li>
          <li>
            <strong>Empruntez</strong> ce dont vous avez besoin pr&egrave;s de chez vous
          </li>
          <li>
            <strong>Restituez</strong> l'article une fois que vous n'en avez plus besoin
          </li>
        </ol>
      </section>

      <section>
        <h2>Nos valeurs</h2>
        <ul>
          <li>
            <strong>Confiance</strong> &mdash; Une communaut&eacute; fond&eacute;e sur la confiance entre parents
          </li>
          <li>
            <strong>Durabilit&eacute;</strong> &mdash; Donner une seconde vie aux objets plut&ocirc;t que d'acheter du neuf
          </li>
          <li>
            <strong>Communaut&eacute;</strong> &mdash; Connecter les familles locales et renforcer les liens de voisinage
          </li>
        </ul>
      </section>
    </Panel>
  </AppPage>
</template>

<style scoped lang="scss">
.logo {
  font-family: "Plus Jakarta Sans", sans-serif;
  font-weight: 200;
  font-size: 3rem;
  margin: 0;
}

.tagline {
  text-align: center;
  color: $text-secondary;
  font-size: 1.1rem;
  margin: 0;
}

section {
  @include flex-column;
  gap: $space-2;

  h2 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0;
  }

  p, li {
    color: $text-secondary;
    line-height: 1.6;
  }

  ol, ul {
    margin: 0;
    padding-left: $space-6;
    @include flex-column;
    gap: $space-2;
  }
}
</style>
```

- [ ] **Step 2: Verify in dev server**

Run: `npm run dev` (or whatever the dev command is — check `package.json`)

Open `/me/about` in browser. Verify:
- Back button works
- Hero shows "Babytroc" + tagline
- Three sections render with correct French content
- Responsive on mobile and desktop

- [ ] **Step 3: Commit**

```bash
git add app/pages/me/about.vue
git commit -m "feat: add content to /me/about page"
```

---

### Task 2: FAQ page (`/me/faq`)

**Files:**
- Modify: `app/pages/me/faq.vue`

- [ ] **Step 1: Replace faq.vue with final content**

Replace the entire file content with:

```vue
<script setup lang="ts">
definePageMeta({
  layout: 'me',
  appBack: true,
  appTitle: 'FAQ',
})

const faq = [
  {
    q: 'Qu\'est-ce que Babytroc\u00a0?',
    a: 'Babytroc est une plateforme lausannoise qui permet aux parents de pr\u00eater et d\'emprunter des articles pour enfants entre particuliers. L\'objectif est de r\u00e9duire le gaspillage et de rendre la parentalit\u00e9 plus accessible.',
  },
  {
    q: 'Comment \u00e7a marche\u00a0?',
    a: 'Cr\u00e9ez un compte, publiez les articles que vous souhaitez pr\u00eater, et parcourez les annonces pour trouver ce dont vous avez besoin. Contactez le pr\u00eateur via la messagerie int\u00e9gr\u00e9e pour organiser l\'emprunt.',
  },
  {
    q: 'Est-ce gratuit\u00a0?',
    a: 'Oui, Babytroc est enti\u00e8rement gratuit. Aucun frais n\'est appliqu\u00e9 pour publier une annonce ou emprunter un article.',
  },
  {
    q: 'Comment cr\u00e9er un compte\u00a0?',
    a: 'Rendez-vous sur la page de connexion et suivez les instructions pour cr\u00e9er votre compte. Vous aurez besoin d\'une adresse email valide.',
  },
  {
    q: 'Comment contacter un pr\u00eateur\u00a0?',
    a: 'Sur la page d\'un article, utilisez le bouton de contact pour envoyer un message au pr\u00eateur via notre messagerie int\u00e9gr\u00e9e.',
  },
  {
    q: 'Que faire en cas de probl\u00e8me avec un article\u00a0?',
    a: 'Contactez-nous via la page Contact. Nous ferons de notre mieux pour vous aider \u00e0 r\u00e9soudre la situation.',
  },
  {
    q: 'Mes donn\u00e9es sont-elles prot\u00e9g\u00e9es\u00a0?',
    a: 'Oui, nous prenons la protection de vos donn\u00e9es tr\u00e8s au s\u00e9rieux. Consultez notre page Politiques pour en savoir plus sur notre politique de confidentialit\u00e9.',
  },
]
</script>

<template>
  <AppPage :max-width="600">
    <Panel>
      <details
        v-for="(item, i) in faq"
        :key="i"
        class="faq-item"
      >
        <summary>{{ item.q }}</summary>
        <p>{{ item.a }}</p>
      </details>
    </Panel>
  </AppPage>
</template>

<style scoped lang="scss">
.faq-item {
  border: 1px solid $border-default;
  border-radius: $radius-sm;
  overflow: hidden;

  summary {
    padding: $space-4;
    font-weight: 600;
    cursor: pointer;
    user-select: none;
    list-style: none;

    &::-webkit-details-marker {
      display: none;
    }

    &::before {
      content: '\25B6';
      display: inline-block;
      margin-right: $space-3;
      font-size: 0.7em;
      transition: transform 200ms ease-out;
    }
  }

  &[open] summary::before {
    transform: rotate(90deg);
  }

  p {
    margin: 0;
    padding: 0 $space-4 $space-4;
    color: $text-secondary;
    line-height: 1.6;
  }
}
</style>
```

- [ ] **Step 2: Verify in dev server**

Open `/me/faq` in browser. Verify:
- 7 questions render as collapsible items
- Click toggles open/close with arrow rotation
- French accents display correctly
- Responsive on mobile and desktop

- [ ] **Step 3: Commit**

```bash
git add app/pages/me/faq.vue
git commit -m "feat: add content to /me/faq page"
```

---

### Task 3: Contact page (`/me/contact`)

**Files:**
- Modify: `app/pages/me/contact.vue`

- [ ] **Step 1: Replace contact.vue with final content**

Replace the entire file content with:

```vue
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
          Une question, un probl&egrave;me ou une suggestion&nbsp;? Contactez-nous&nbsp;!
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
            <p>Merci&nbsp;! Votre message a bien &eacute;t&eacute; envoy&eacute;.</p>
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
```

- [ ] **Step 2: Verify in dev server**

Open `/me/contact` in browser. Verify:
- Intro text and email link render
- Form displays 4 fields + submit button
- Submit button is disabled when fields are empty
- Filling all fields and clicking "Envoyer" shows success message
- "Envoyer un autre message" resets back to the form
- Email field requires `@` character
- Responsive on mobile and desktop

- [ ] **Step 3: Commit**

```bash
git add app/pages/me/contact.vue
git commit -m "feat: add content to /me/contact page"
```

---

### Task 4: Politiques page (`/me/politics`)

**Files:**
- Modify: `app/pages/me/politics.vue`

- [ ] **Step 1: Replace politics.vue with final content**

Replace the entire file content with:

```vue
<script setup lang="ts">
definePageMeta({
  layout: 'me',
  appBack: true,
  appTitle: 'Politiques',
})
</script>

<template>
  <AppPage :max-width="600">
    <Panel>
      <section>
        <h2>Conditions d'utilisation</h2>
        <ul>
          <li>
            Babytroc est une plateforme de mise en relation entre particuliers
            pour le pr&ecirc;t d'articles pour enfants.
          </li>
          <li>
            L'utilisateur est responsable de l'exactitude des informations
            publi&eacute;es sur ses annonces.
          </li>
          <li>
            Les articles propos&eacute;s doivent &ecirc;tre en bon &eacute;tat
            et conformes &agrave; leur description.
          </li>
          <li>
            Babytroc n'est pas responsable des transactions entre utilisateurs.
          </li>
          <li>
            Babytroc se r&eacute;serve le droit de supprimer tout contenu ne
            respectant pas les r&egrave;gles de la communaut&eacute;.
          </li>
        </ul>
      </section>

      <section>
        <h2>Politique de confidentialit&eacute;</h2>
        <ul>
          <li>
            <strong>Donn&eacute;es collect&eacute;es&nbsp;:</strong> adresse email,
            informations de profil et donn&eacute;es d'utilisation.
          </li>
          <li>
            <strong>Utilisation&nbsp;:</strong> gestion du compte, communication
            entre utilisateurs et am&eacute;lioration du service.
          </li>
          <li>
            <strong>Partage&nbsp;:</strong> vos donn&eacute;es ne sont jamais
            vendues &agrave; des tiers.
          </li>
          <li>
            <strong>Vos droits&nbsp;:</strong> vous pouvez demander l'acc&egrave;s,
            la modification ou la suppression de vos donn&eacute;es en nous
            contactant.
          </li>
          <li>
            <strong>S&eacute;curit&eacute;&nbsp;:</strong> vos donn&eacute;es sont
            stock&eacute;es de mani&egrave;re s&eacute;curis&eacute;e.
          </li>
        </ul>
      </section>

      <section>
        <h2>R&egrave;gles de la communaut&eacute;</h2>
        <ul>
          <li>Seuls les articles pour enfants sont autoris&eacute;s.</li>
          <li>
            Les articles doivent &ecirc;tre propres, fonctionnels et conformes
            &agrave; leur description.
          </li>
          <li>
            <strong>R&egrave;gles pour les photos&nbsp;:</strong>
            <ul>
              <li>
                Aucune personne ne doit appara&icirc;tre sur les photos
                (ni adulte, ni enfant, ni b&eacute;b&eacute;).
              </li>
              <li>
                &Eacute;viter de montrer excessivement l'espace priv&eacute;
                (int&eacute;rieur du domicile).
              </li>
              <li>
                Aucun contenu &agrave; caract&egrave;re sexuel, haineux ou
                d&eacute;go&ucirc;tant.
              </li>
            </ul>
          </li>
          <li>
            La communication entre utilisateurs doit rester respectueuse et
            bienveillante.
          </li>
          <li>Toute activit&eacute; commerciale est interdite.</li>
          <li>
            Le non-respect de ces r&egrave;gles peut entra&icirc;ner la suspension
            ou la suppression du compte.
          </li>
        </ul>
      </section>
    </Panel>
  </AppPage>
</template>

<style scoped lang="scss">
section {
  @include flex-column;
  gap: $space-2;

  h2 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0;
  }

  ul {
    margin: 0;
    padding-left: $space-6;
    @include flex-column;
    gap: $space-2;
  }

  li {
    color: $text-secondary;
    line-height: 1.6;
  }

  li > ul {
    margin-top: $space-2;
  }
}
</style>
```

- [ ] **Step 2: Verify in dev server**

Open `/me/politics` in browser. Verify:
- Three sections render: Conditions, Confidentialit&eacute;, R&egrave;gles
- Photo rules appear as a nested sub-list
- French accents display correctly
- Responsive on mobile and desktop

- [ ] **Step 3: Commit**

```bash
git add app/pages/me/politics.vue
git commit -m "feat: add content to /me/politics page"
```
