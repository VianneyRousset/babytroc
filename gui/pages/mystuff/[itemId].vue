<script setup lang="ts">

const route = useRoute();
const itemId = route.params.itemId;

const { data, refresh } = await useFetch(`/api/myitems/${itemId}`);

async function acceptRequest(borrowerId: string) {

  await $fetch(`/api/myitems/${itemId}/requests/${borrowerId}/accept`, {
    method: "POST",
  })

  await refresh();
}

async function declineRequest(borrowerId: string) {

  await $fetch(`/api/myitems/${itemId}/requests/${borrowerId}/decline`, {
    method: "POST",
  })

  await refresh();
}

async function terminateLoan() {

  await $fetch(`/api/loans/${data.value.item.activeLoan.id}/terminate`, {
    method: "POST",
  });

  await refresh();

}

</script>

<template>
  <main>

    <section>
      <div class="content row">
        <ItemPreview :item="data?.item" class="img" />
        <div class="info">
          <div>
            <h2>{{ data?.item.name }}</h2>
            <p>{{ data?.item.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="data?.item.activeLoan || data?.item.loanRequests.length">
      <div class="header">
        <h2>Demandes et prêts</h2>
      </div>
      <div class="content">
        <div class="active-loan" v-if="data?.item.activeLoan">
          <div>Prêté à <span style="font-weight: 600;">{{ data?.item.activeLoan.borrower.name }}</span> depuis le {{
            data?.item.activeLoan.startAt }}</div>
          <button class="bezel" @click="terminateLoan()">Terminer</button>
        </div>
        <ul v-if="data?.item.loanRequests.length">

          <li v-for="request in data?.item.loanRequests">
            <div class="user">
              <UserThumb :user="request.borrower" :size=40 />
              <div>{{ request.borrower.name }}</div>
            </div>
            <div class="date">Demandé le {{ request.createdAt }}</div>
            <div>
              <button class="outline neutral" @click="declineRequest(request.borrower.id)">Refuser</button>
              <button :disabled="data?.item.activeLoan" class="bezel"
                @click="acceptRequest(request.borrower.id)">Accepter</button>
            </div>
          </li>
        </ul>
      </div>
    </section>

  </main>
</template>

<style scoped>
.item-info {
  display: flex;
  flex-direction: row;
  gap: 2rem;
}

.info {
  display: flex;
  flex-direction: column;
}

.img {
  width: 24rem;
  height: 24rem;
}

h2 {
  font-weight: medium;
  font-size: 2rem;
  color: var(--neutral-800);
  margin: 0;
}

p {
  color: var(--neutral-500);
  font-size: 1.2rem;
  width: 24rem;
}


.active-loan {
  font-weight: 400;
  color: var(--brand-400);
  padding: 1rem 2rem;
  border-radius: 1rem;
  border: 1px solid var(--brand-400);
  background: var(--brand-50);
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

ul {
  border-top: 1px solid var(--neutral-200);
  padding: 0;
  margin: 0;
}

ul li {
  display: flex;
  gap: 2rem;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--neutral-200);
}

ul li>* {
  display: flex;
  align-items: center;
  gap: 1rem;
}

li .user {
  color: var(--neutral-800);
  font-weight: 500;
  font-size: 1.2rem;
}

li .date {
  color: var(--neutral-600);
}

input,
textarea {
  width: 20rem;
  resize: none;
  font-family: "Inter", sans-serif;
  font-size: 1rem;
  border-radius: 0.5rem;
  border: 1px solid var(--neutral-500);
  padding: 0.4rem;
}

textarea {
  flex-grow: 1;
}

@media only screen and (max-width: 50rem) {
  .item-info {
    flex-direction: column;
  }

  .img {
    width: 100%;
  }

  ul li {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }


}
</style>
