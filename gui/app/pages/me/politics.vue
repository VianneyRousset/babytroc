<script setup lang="ts">
definePageMeta({
  layout: 'me',
  appBack: true,
  appTitle: 'Politiques',
})
</script>

<template>
  <AppPage
    with-header
    :max-width="600"
  >
    <main>
      <section class="card">
        <h2>Conditions d'utilisation</h2>
        <ul>
          <li>
            Babytroc est une plateforme de mise en relation entre particuliers
            pour le prêt d'articles pour enfants.
          </li>
          <li>
            L'utilisateur est responsable de l'exactitude des informations
            publiées sur ses annonces.
          </li>
          <li>
            Les articles proposés doivent être en bon état
            et conformes à leur description.
          </li>
          <li>
            Babytroc n'est pas responsable des transactions entre utilisateurs.
          </li>
          <li>
            Babytroc se réserve le droit de supprimer tout contenu ne
            respectant pas les règles de la communauté.
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>Politique de confidentialité</h2>
        <ul>
          <li>
            <strong>Données collectées&nbsp;:</strong> adresse email,
            informations de profil et données d'utilisation.
          </li>
          <li>
            <strong>Utilisation&nbsp;:</strong> gestion du compte, communication
            entre utilisateurs et amélioration du service.
          </li>
          <li>
            <strong>Partage&nbsp;:</strong> vos données ne sont jamais
            vendues à des tiers.
          </li>
          <li>
            <strong>Vos droits&nbsp;:</strong> vous pouvez demander l'accès,
            la modification ou la suppression de vos données en nous
            contactant.
          </li>
          <li>
            <strong>Sécurité&nbsp;:</strong> vos données sont
            stockées de manière sécurisée.
          </li>
        </ul>
      </section>

      <section class="card">
        <h2>Règles de la communauté</h2>
        <ul>
          <li>Seuls les articles pour enfants sont autorisés.</li>
          <li>
            Les articles doivent être propres, fonctionnels et conformes
            à leur description.
          </li>
          <li>
            <strong>Règles pour les photos&nbsp;:</strong>
            <ul>
              <li>
                Aucune personne ne doit apparaître sur les photos
                (ni adulte, ni enfant, ni bébé).
              </li>
              <li>
                Éviter de montrer excessivement l'espace privé
                (intérieur du domicile).
              </li>
              <li>
                Aucun contenu à caractère sexuel, haineux ou
                dégoûtant.
              </li>
            </ul>
          </li>
          <li>
            La communication entre utilisateurs doit rester respectueuse et
            bienveillante.
          </li>
          <li>Toute activité commerciale est interdite.</li>
          <li>
            Le non-respect de ces règles peut entraîner la suspension
            ou la suppression du compte.
          </li>
        </ul>
      </section>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
main {
  @include flex-column;
  gap: $space-4;
  padding: $space-4;
}

.card {
  @include flex-column;
  gap: $space-2;
  background: $bg-surface;
  border-radius: $radius-md;
  box-shadow: $shadow-sm;
  padding: $space-4;

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
