<script setup lang="ts">

// TODO do not use user id for thumb seed

const { data } = await useFetch('/api/account');

</script>

<template>
  <div>
    <UserThumb :user="data.user" :size=40 />
    <span>{{ data.user.name }}</span>
  </div>
</template>

<style scoped>
div {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 1.2rem;
  transition: transform 0.1s ease-out;
}

img {
  margin-right: 0.5rem;
}

span {
  color: #7f7878;
  opacity: 50%;
  white-space: nowrap;
  transition: opacity 0.1s ease-out;
}

div:hover {
  transform: scale(1.1);
}

div:hover span {
  opacity: 100%;
}
</style>
