<script setup lang="ts">
import { Bookmark, BookmarkX, ShieldAlert } from 'lucide-vue-next'

const props = defineProps<{
  item: Item | ItemPreview
  savedItems: Array<Item | ItemPreview>
}>()

const { item, savedItems } = toRefs(props)

const { isSavedByUser } = useItemSave(item, savedItems)

const { mutate: saveItem } = useSaveItemMutation()
const { mutate: unsaveItem } = useUnsaveItemMutation()
</script>

<template>
  <DropdownMenu>
    <!-- Unsave -->
    <DropdownMenuItem
      v-if="isSavedByUser"
      @click="unsaveItem(item.id)"
    >
      <BookmarkX
        :size="32"
        :stroke-width="2"
      />
      <div>Oublier</div>
    </DropdownMenuItem>

    <!-- Save -->
    <DropdownMenuItem
      v-else
      @click="saveItem(item.id)"
    >
      <Bookmark
        :size="32"
        :stroke-width="2"
      />
      <div>Enregistrer</div>
    </DropdownMenuItem>

    <!-- Report -->
    <DropdownMenuItem class="red">
      <ShieldAlert
        :size="32"
        :stroke-width="2"
      />
      <div>Signaler</div>
    </DropdownMenuItem>
  </DropdownMenu>
</template>
