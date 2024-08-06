<script setup lang="ts">
definePageMeta({
  layout: "minimal",
});

function enterSession(token: string) {
  const config = useRuntimeConfig();

  useCookie("token", {
    sameSite: true,
    maxAge: config.public.cookieDuration,
  }).value = token;

  navigateTo("/explore");
}

</script>

<template>
  <div>
    <LoginBox @login="enterSession($event)" />
  </div>
</template>
