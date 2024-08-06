<script setup>
const props = defineProps(['name', 'status'])
</script>

<template>
  <div class="row">
    <div class="image">
      <img src="/img/tmp.jpg" />
    </div>
    <div class="info">
      <h1>{{ name }}</h1>
    </div>
    <div class="status">
      {{ status }}
    </div>
  </div>
</template>

<style scoped>
.row {
  display: flex;
  padding: 16px;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
}

.image {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 50%;
  margin-right: 28px;
}

img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info {
  flex-grow: 1;
  color: #7f7878;
}

.info h1 {
  font-weight: initial;
  font-size: clamp(1.3rem, 0.1rem + 2vw, 2.1rem);
}





@media only screen and (max-width: 800px) {
  #box>div {
    margin-top: 12em;
    margin-left: 2em;
  }
}
</style>
