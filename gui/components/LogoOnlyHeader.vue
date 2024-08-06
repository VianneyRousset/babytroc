<template>
  <header>
    <NuxtLink to="/">
      <img src="/img/logo.svg" />
    </NuxtLink>
  </header>
</template>

<style scoped>
header {
  display: flex;
  padding: 30px 40px;
}

@media only screen and (max-width: 800px) {
  header {
    justify-content: center;
  }
}
</style>
