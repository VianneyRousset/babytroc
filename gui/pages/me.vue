<script setup lang="ts">

const { arg, status, asyncStatus, data, error, loadMore } = useTestInfiniteQuery();

const input = ref("");

function submit() {
  arg.value = unref(input);
}

</script>

<template>
  <div>
    <SearchInput v-model="input" @submit="submit()" />
    <ul @click="loadMore">
      <li>arg: {{ arg }}</li>
      <li>{{ status }}</li>
      <li>{{ asyncStatus }}</li>
      <li>data: {{ data.data }}</li>
      <li>cursor: {{ data.cursor }}</li>
      <li>{{ error }}</li>
    </ul>
  </div>
</template>
