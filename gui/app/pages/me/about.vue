<script setup lang="ts">
definePageMeta({
	layout: "me",
	appBack: true,
	appTitle: "A propos",
});
</script>

<template>
  <AppPage
    with-header
    :max-width="600"
  >
    <main>
      <PanelBanner>
        <h1 class="logo">
          Babytroc
        </h1>
        <p class="tagline">
          La plateforme lausannoise de prêt d'articles pour enfants entre particuliers.
        </p>
      </PanelBanner>

      <section class="section">
        <h2>Notre mission</h2>
        <p>
          Babytroc est née d'une idée simple : les enfants grandissent vite,
          mais leurs affaires peuvent encore servir. Notre mission est de réduire le
          gaspillage, renforcer la confiance entre parents et rendre la parentalité
          plus accessible en facilitant le prêt d'articles pour enfants entre familles.
        </p>
      </section>

      <hr class="divider">

      <section class="section">
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

      <hr class="divider">

      <section class="section">
        <h2>Nos valeurs</h2>
        <ul>
          <li>
            <strong>Confiance :</strong> une communauté fondée sur la confiance entre parents
          </li>
          <li>
            <strong>Durabilité :</strong> donner une seconde vie aux objets plutôt que d'acheter du neuf
          </li>
          <li>
            <strong>Communauté :</strong> connecter les familles locales et renforcer les liens de voisinage
          </li>
        </ul>
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

.logo {
  font-family: "Plus Jakarta Sans", sans-serif;
  font-weight: 200;
  font-size: 3rem;
  margin: 0;
  text-align: center;
}

.tagline {
  text-align: center;
  color: $text-secondary;
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
}

:deep(.PanelBanner) {
  padding: 3rem 0;

  h1 {
    margin-bottom: 0.75em;
  }
}

.divider {
  border: none;
  border-top: 1px solid $divider;
  margin: $space-2 0;
}

.section {
  @include flex-column;
  align-items: stretch;
  gap: $space-3;
  padding: $space-6 0;

  h2 {
    font-family: "Plus Jakarta Sans", sans-serif;
    font-size: 1.25rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin: 0;
  }

  p {
    margin: 0;
    color: $text-secondary;
    line-height: 1.6;
  }

  li {
    color: $text-secondary;
    line-height: 1.6;
  }

  ol, ul {
    margin: 0;
    padding-left: 0;
    list-style: none;
    @include flex-column;
    gap: $space-2;
  }

  ol {
    counter-reset: steps;

    li {
      counter-increment: steps;

      &::before {
        content: counter(steps) ". ";
        font-weight: 600;
        color: $text-tertiary;
      }
    }
  }

  ul li::before {
    content: "\2022\00a0";
    color: $text-tertiary;
  }
}
</style>
