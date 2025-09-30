<script setup lang="ts" generic="T extends {active_loan?: Loan | null}">
import VSwitch from '@lmiller1990/v-switch'
import { Box } from 'lucide-vue-next'

const props = defineProps<{
  item: T
}>()

const { item } = toRefs(props)

const state = computed<'loaned' | 'owned' | 'borrowed' | 'requested' | undefined>(() => {
  const _item = unref(item)
  return _item.owned
    ? (_item.active_loan ? 'loaned' : 'owned')
    : (_item.active_loan ? 'borrowed' : (_item.active_loan_request ? 'requested' : undefined))
})
</script>

<template>
  <div class="ItemInfoBoxes">
    <v-switch :case="state">
      <!-- Loaned -->
      <template #loaned>
        <NuxtLink :to="`/chats/${item.active_loan.chat_id}`">
          <InfoBox
            chevron-right
            :icon="Box"
          >
            Vous avez prété cet objet à {{ item.active_loan.borrower.name }}
            <template #mini>
              {{ formatRelativeDateRange(item.active_loan.during) }}
            </template>
          </InfoBox>
        </NuxtLink>
      </template>

      <!-- Owned -->
      <template #owned>
        <InfoBox :icon="Box">
          Cet objet vous appartient.
        </InfoBox>
      </template>

      <!-- Borrowed -->
      <template #borrowed>
        <NuxtLink :to="`/chats/${item.active_loan.chat_id}`">
          <InfoBox
            chevron-right
            :icon="Box"
          >
            Vous avez emprunté cet objet.
            <template #mini>
              {{ formatRelativeDateRange(item.active_loan.during) }}
            </template>
          </InfoBox>
        </NuxtLink>
      </template>

      <!-- requested -->
      <template #requested>
        <NuxtLink :to="`/chats/${item.active_loan_request.chat_id}`">
          <InfoBox
            chevron-right
            :icon="Box"
          >
            Vous avez demandé à emprunté cet objet.
          </InfoBox>
        </NuxtLink>
      </template>
    </v-switch>
  </div>
</template>

<style scoped lang="scss">
a {
  @include reset-link;
}
</style>
