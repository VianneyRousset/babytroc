<script setup lang="ts">

import { ChevronRight } from 'lucide-vue-next';

// TODO move types into /types/index.ts

const props = defineProps<{
  chat: Chat,
}>();

// chat
const { chat } = toRefs(props);
const { interlocutor, item } = useChat(chat);

// interlocutor
const { name: interlocutorName, avatarSeed: interlocutorAvatar } = useUserPreview(interlocutor);

// item
const { name: itemName, firstImagePath: itemImagePath } = useItemPreview(item);


</script>

<template>
  <div class="ChatSlab">

    <ImageAndAvatar :image="itemImagePath" :avatar="interlocutorAvatar" />

    <div class="name">
      <div>{{ interlocutorName ?? "..." }}</div>
      <div>{{ itemName ?? "..." }}</div>
    </div>

    <ChevronRight :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />

  </div>

</template>

<style scoped lang="scss">
.ChatSlab {

  @include flex-row;
  gap: 1rem;
  justify-content: flex-start;
  padding: 1rem;

  color: $neutral-300;

  .image {
    width: 64px;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .name {
    @include flex-column;
    align-items: stretch;
    gap: 4px;
    flex: 1;

    font-family: "Plus Jakarta Sans";
    overflow: hidden;

    div:first-child {
      @include ellipsis-overflow;
      color: $neutral-900;
      font-size: 1.2rem;
    }

    div:last-child {
      @include ellipsis-overflow;
      color: $neutral-400;
    }
  }
}
</style>
