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
          La plateforme lausannoise de prêt d'articles pour enfants entre particuliers.
        </p>
      </PanelBanner>

      <section>
        <h2>Notre mission</h2>
        <p>
          Babytroc est née d'une idée simple : les enfants grandissent vite,
          mais leurs affaires peuvent encore servir. Notre mission est de réduire le
          gaspillage, renforcer la confiance entre parents et rendre la parentalité
          plus accessible en facilitant le prêt d'articles pour enfants entre familles.
        </p>
      </section>

      <section>
        <h2>Comment ça marche</h2>
        <ol>
          <li>
            <strong>Publiez</strong> vos articles pour enfants que vous n'utilisez plus
          </li>
          <li>
            <strong>Empruntez</strong> ce dont vous avez besoin près de chez vous
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
            <strong>Confiance</strong> — Une communauté fondée sur la confiance entre parents
          </li>
          <li>
            <strong>Durabilité</strong> — Donner une seconde vie aux objets plutôt que d'acheter du neuf
          </li>
          <li>
            <strong>Communauté</strong> — Connecter les familles locales et renforcer les liens de voisinage
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
