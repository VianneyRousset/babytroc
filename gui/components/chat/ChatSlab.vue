<script setup lang="ts">
import { ChevronRight } from "lucide-vue-next";

const props = defineProps<{
	chat: Chat;
	me: User;
}>();

// chat
const { chat, me } = toRefs(props);

// interlocutor
const { interlocutor } = useChatRoles(chat, me);

// item image
const { firstImagePath: itemImage } = useItemFirstImage(
	computed(() => unref(chat).item),
);
</script>

<template>
  <Slab>

    {{ interlocutor.name }}

    <template #image>
      <ImageAndAvatar :image="itemImage" :avatar="interlocutor.avatar_seed" />
    </template>

    <template #sub>
      {{ chat.item.name }}
    </template>

  </Slab>
</template>
