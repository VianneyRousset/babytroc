<script setup lang="ts">
const props = defineProps<{
  chat: Chat
  me: UserPrivate
}>()

// chat
const { chat, me } = toRefs(props)

// interlocutor
const { interlocutor } = useChatRoles(chat, me)

// item image
const { firstImagePath: itemImage } = useItemFirstImage(
  computed(() => unref(chat).item),
)

// has new messages
const { hot } = useChatHot(chat)
</script>

<template>
  <Slab>
    {{ chat.item.name }}

    <template #image>
      <ImageAndAvatar
        :image="itemImage"
        :avatar="interlocutor.avatar_seed"
      />
    </template>

    <template #sub>
      {{ interlocutor.name }}
    </template>

    <template
      v-if="hot"
      #badge
    />
  </Slab>
</template>
