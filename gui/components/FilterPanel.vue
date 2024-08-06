<template>
  <div class="filters">
    <div>Search</div>
    <div>Regions</div>
    <div>Availability</div>
  </div>
</template>

<style scoped>
.navigator {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  padding: 1em;
  grid-gap: 1em;
}

@media only screen and (max-width: 1000px) {
  .navigator {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}

@media only screen and (max-width: 800px) {
  .navigator {
    padding: 1em 2em;
    display: flex;
    flex-direction: column;
  }
}
</style>
