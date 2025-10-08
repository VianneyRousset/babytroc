<script setup lang="ts">
const props = defineProps<{
  chat: Chat
  me: UserPrivate
}>()

// chat
const { chat, me } = toRefs(props)

// interlocutor
const { isUserBorrowing, interlocutor } = useChatRoles(chat, me)

// item image
const { firstImagePath: itemImage } = useItemFirstImage(
  computed(() => unref(chat).item),
)

// has new messages
const { hasUnseenMessageForMe } = useChatSeen(chat, me)
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
      {{ isUserBorrowing ? `Pour emprunter à ${interlocutor.name}` : `Pour prêter à ${interlocutor.name}` }}
    </template>

    <template
      v-if="hasUnseenMessageForMe"
      #badge
    />
  </Slab>
</template>
