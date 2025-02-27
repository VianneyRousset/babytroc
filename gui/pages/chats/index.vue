<script setup lang="ts">

const store = useChatsStore();

function loadMore() {
  store.more();
}

</script>

<template>
  <div>
    <ul>
      <li v-for="chat in store.chats">
        <!--<ImageAndAvatar :image="chat.item.first_image_name" :avatar="chat.borrower.avatar_seed" />-->
      </li>
    </ul>

    <button @click="loadMore">More</button>
  </div>
</template>

<style lang="scss" scoped></style>
