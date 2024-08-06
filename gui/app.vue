<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>

<style>
.page-enter-active,
.page-leave-active {
  transition: all 0.4s;
}

.page-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.page-enter-to,
.page-leave-from {
  transform: translateX(0%);
  opacity: 1;
}

.page-leave-to {
  transform: translateX(-100%);
  opacity: 0;
}
</style>
