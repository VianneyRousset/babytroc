<script setup lang="ts">

import { Gift } from 'lucide-vue-next';

const model = defineModel<boolean>();

const props = defineProps<{
  item: Item | ItemPreview,
  user: User | UserPreview,
  loanRequestId: number,
}>();

// chat
const { item, user, loanRequestId } = toRefs(props);

// mutations
const { mutateAsync: acceptLoanRequest, asyncStatus: acceptLoanRequestAsyncStatus } = useAcceptLoanRequestMutation();
</script>

<template>
  <Overlay v-model="model">
    <Popup v-model="model">
      <Gift :size="128" :strokeWidth="4" :absoluteStrokeWidth="true" />
      <div>Êtes-vous sûr d'accepter de prêter l'objet <b>{{ item.name }}</b> à <b>{{ user.name }}</b> ?</div>
      <TextButton aspect="flat" size="large" color="primary" :loading="acceptLoanRequestAsyncStatus === 'loading'"
        @click="acceptLoanRequest({ itemId: item.id, loanRequestId: loanRequestId })">Accepter</TextButton>
    </Popup>
  </Overlay>
</template>
