<script setup lang="ts">
import { RefreshCw } from "lucide-vue-next";

definePageMeta({
	layout: "me",
	appBack: true,
	appTitle: "Profile",
});

const { me } = useMe();
const { mutateAsync: updateProfile, isLoading } = useUpdateProfileMutation();
const { $toast } = useNuxtApp();

function randomSeed() {
	const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
	const length = 5 + Math.floor(Math.random() * 6); // 5-10 chars
	return Array.from(
		{ length },
		() => chars[Math.floor(Math.random() * chars.length)],
	).join("");
}

async function regenerateAvatar() {
	await updateProfile({ avatar_seed: randomSeed() }).catch(() => {
		$toast.error("Échec de la mise à jour");
	});
}
</script>

<template>
  <AppPage logged-in-only>
    <main>
      <Panel>
        <WithLoading :loading="!me">
          <div
            v-if="me"
            class="profile"
          >
            <!-- Avatar -->
            <div class="avatar-section">
              <UserAvatar
                :seed="me.avatar_seed"
                :size="120"
              />
              <h1>{{ me.name }}</h1>
              <TextButton
                aspect="outline"
                size="small"
                :icon="RefreshCw"
                :loading="isLoading"
                @click="regenerateAvatar"
              >
                Nouvel avatar
              </TextButton>
            </div>

            <!-- Stats -->
            <div class="stats">
              <div class="stat">
                <span class="value">{{ me.stars_count }}</span>
                <span class="label">Étoiles</span>
              </div>
              <div class="stat">
                <span class="value">{{ me.likes_count }}</span>
                <span class="label">Likes</span>
              </div>
              <div class="stat">
                <span class="value">{{ me.items_count }}</span>
                <span class="label">Objets</span>
              </div>
            </div>
          </div>
        </WithLoading>
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
.profile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $space-8;
  padding: $space-10 $space-4;

  .avatar-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $space-4;

    h1 {
      font-family: "Plus Jakarta Sans", sans-serif;
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }
  }

  .stats {
    display: flex;
    gap: 0;

    .stat {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0 $space-8;
      gap: $space-1;

      &:not(:last-child) {
        border-right: 1px solid $divider;
      }

      .value {
        @include font-jakarta;
        font-size: 1.25rem;
        font-weight: 700;
        color: $text-primary;
      }

      .label {
        font-size: 0.8rem;
        color: $text-secondary;
      }
    }
  }
}
</style>
