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
