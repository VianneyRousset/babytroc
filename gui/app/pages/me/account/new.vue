<script setup lang="ts">
import { UserRound } from 'lucide-vue-next'

const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

const name = ref("")
const email = ref("")
const password = ref("")
const passwordConfirm = ref("")
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="main-header">
      <AppBack />
      <h1>Créer un compte</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main>
      <!-- Not logged in: show login form -->
      <div class="app-content page">
        <UserRound
          :size="48"
          :stroke-width="2"
        />
        <MeAccountName v-model="name" />
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}

.lock {
  @include flex-column-center;
  gap: 1rem;
  height: 8rem;
  width: 100%;
  color: $neutral-800;

  &.red {
    color: $red-800;
  }
}

.form {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;

  input {
    border-radius: 0.5rem;
    padding: 0.6rem 1.5rem;
    font-size: 1.5rem;
  }
}

.hr-container {
  @include flex-row;
  gap: 1rem;
  padding:  1rem;
  color: $neutral-400;
  font-family: "Plus Jakarta Sans", sans-serif;
  hr {
    flex: 1;
    border: none;
    border-top: 1px solid $neutral-400;
  }
}

.create-account-button {
  @include reset-link;
  text-align: center;
  cursor: pointer;
  font-size: 1.5rem;
  padding: 0.6rem 1.5rem;
  color: $neutral-400;
}
</style>
