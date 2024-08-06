<script setup lang="ts">

const { data } = await useFetch("/api/myitems", {
  method: "GET",
});

const items = data.value.items;

</script>

<template>
  <div class="items-list">
    <div class="header">
      <p>My items</p>
      <button class="flat">Add item</button>
    </div>
    <ItemListRow v-for="item in items" :key="item.id" :name="item.name" status="available" />
  </div>
</template>

<style scoped>
.header {
  border: 1px solid red;
  font-size: 36px;
  color: #7f7878;
  border-bottom: 1px solid #ccbfbf;
  padding: 16px;
}

.header button {}

.items-list {
  display: flex;
  flex-direction: column;
}
</style>
