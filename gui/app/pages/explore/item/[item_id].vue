<script setup lang="ts">
import { Pencil, ShieldAlert, X, Trash } from 'lucide-vue-next'

definePageMeta({
  layout: 'explore',
})

// get item ID from route
const route = useRoute()
const itemId = Number.parseInt(route.params.item_id as string) // TODO avoid this hack
const { currentTab } = useTab()

// goto tab main page if invalid itemId
if (Number.isNaN(itemId)) navigateTo(`/${currentTab}`)

// query item
const { item, isLoading } = useItem({ itemId })

// auth
const { loggedIn } = useAuth()

const editMode = ref(false)

const device = useDevice()

const { goBack } = useNavigation()
const deleteItemPopup = ref(false)

const { $toast } = useNuxtApp()
const { mutateAsync: updateItem, isLoading: updateItemIsLoading } = useUpdateItemMutation(itemId)
const { mutateAsync: deleteItem, isLoading: deleteItemIsLoading } = useDeleteItemMutation(itemId)

async function submitUpdateItem(data: ItemUpdate) {
  await updateItem(data).catch((err) => {
    $toast.error('Échec de la modification de l\'objet')
    throw err
  })
  editMode.value = false
}

async function submitDeleteItem() {
  await deleteItem().catch((err) => {
    $toast.error('Échec de la suppression de l\'objet')
    throw err
  })
  return goBack()
}
</script>

<template>
  <AppPage
    with-header
    :max-width="1000"
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack />
      <h1 :title="item?.name">
        {{ item?.name }}
      </h1>

      <!-- Dropdown menu -->
      <DropdownMenu v-if="loggedIn === true && item">
        <DropdownItem
          v-if="item.owned"
          :icon="Pencil"
          @click="() => (editMode = true)"
        >
          Modifier
        </DropdownItem>
        <DropdownItem
          v-if="item.owned"
          :icon="Trash"
          red
          @click="() => (deleteItemPopup = true)"
        >
          Supprimer
        </DropdownItem>
        <DropdownItem
          v-if="!item.owned"
          :icon="ShieldAlert"
          red
        >
          Signaler
        </DropdownItem>
      </DropdownMenu>
    </template>

    <!-- Mobile page -->
    <template #mobile>
      <main>
        <WithLoading :loading="!item && isLoading">
          <!-- View -->
          <Panel v-if="item && !editMode">
            <ItemImagesGallery :item="item" />
            <div class="name-description">
              <h1>{{ item.name }}</h1>
              <p class="description">
                {{ item.description }}
              </p>
            </div>
            <ItemInfoBox :item="item" />
            <ItemOwner
              :item="item"
              :target="userId => `/explore/user/${userId}`"
            />
            <h2>Informations</h2>
            <ItemMinitable
              v-if="device.isMobile"
              :item="item"
            />
            <ItemRegionsMap :item="item" />
            <ItemRequestButton :item="item" />
          </Panel>

          <!-- Edit -->
          <Panel
            v-else-if="editMode"
            :max-width="600"
          >
            <ItemEditionForm
              :item="item"
              :is-loading="updateItemIsLoading"
              @submit="submitUpdateItem"
            />
          </Panel>
        </WithLoading>
      </main>
    </template>

    <!-- Desktop page -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack v-if="!editMode" />
          <IconButton
            v-else
            :icon="X"
            @click="() => (editMode = false)"
          />
        </template>

        <template #buttons-right>
          <DropdownMenu v-if="loggedIn === true && item && !editMode">
            <DropdownItem
              v-if="item.owned"
              :icon="Pencil"
              @click="() => (editMode = true)"
            >
              Modifier
            </DropdownItem>
            <DropdownItem
              v-if="item.owned"
              :icon="Trash"
              red
              @click="() => (deleteItemPopup = true)"
            >
              Supprimer
            </DropdownItem>
            <DropdownItem
              v-if="!item.owned"
              :icon="ShieldAlert"
              red
            >
              Signaler
            </DropdownItem>
          </DropdownMenu>
        </template>
      </AppHeaderDesktop>
      <main>
        <!-- View -->
        <WithLoading :loading="!item && isLoading">
          <Panel
            v-if="item && !editMode"
            class="desktop"
          >
            <ItemImagesGallery
              :item="item"
              wide
            />
            <section
              class="h golden-left"
              style="gap: 2em;"
            >
              <div class="name-description">
                <h1>{{ item.name }}</h1>
                <p>{{ item.description }}</p>
                <ItemAge
                  :item="item"
                  :lowercase="true"
                  prefix="Convient à des enfants "
                />
              </div>
              <div class="v">
                <ItemInfoBox :item="item" />
                <ItemOwner
                  :item="item"
                  :chevron="true"
                  :target="userId => `/explore/user/${userId}`"
                />
                <ItemRequestButton :item="item" />
              </div>
            </section>
            <section>
              <h2>Régions</h2>
              <div class="h golden-left">
                <ItemRegionsList :item="item" />
                <ItemRegionsMap :item="item" />
              </div>
            </section>
          </Panel>

          <!-- Edit -->
          <Panel
            v-else-if="editMode"
            :max-width="600"
          >
            <ItemEditionForm
              :item="item"
              :is-loading="updateItemIsLoading"
              @submit="submitUpdateItem"
            />
          </Panel>
        </WithLoading>
      </main>
    </template>

    <!-- Delete item popup -->
    <PopupOverlay v-model="deleteItemPopup">
      <Trash
        :size="128"
        :stroke-width="1"
      />
      <div>Êtes-vous sûr de supprimer l'objet <b>{{ item?.name }}</b> ? Cette opération est irréversible.</div>
      <template #actions>
        <TextButton
          aspect="flat"
          size="large"
          color="red"
          :loading="deleteItemIsLoading"
          @click="submitDeleteItem"
        >
          Supprimer
        </TextButton>
        <TextButton
          aspect="outline"
          size="large"
          color="neutral"
          @click="deleteItemPopup = false"
        >
          Annuler
        </TextButton>
      </template>
    </PopupOverlay>
  </AppPage>
</template>

<style scoped lang="scss">
:deep(.Panel.desktop .content) {

  gap: 2em;

  .name-description {
    h1 {
      margin: 0;
    }
  }

  section {
    font-size: clamp(0.6em, 2vw, 1em);

    .ItemAge {
      color: $neutral-400;
      font-style: italic;
    }

    .ItemRegionsList {
      font-size: clamp(0.6em, 1.4vw, 0.8em);
      padding: 2em 0;
    }
  }
}

.LoadingAnimation {
  width: 100%;
  height: 10em;
}
</style>
