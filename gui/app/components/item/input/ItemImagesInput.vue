<script setup lang="ts">
import { OctagonAlert, Check } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  msgPlacement?: MsgPlacement
  uploadStatus?: 'idle' | 'pending' | 'success' | 'error'
}>(), {
  uploadStatus: 'idle',
})

const { msgPlacement } = toRefs(props)

const images = defineModel<Array<string>>('images', { default: [] })
const valid = defineModel<boolean>('valid', { default: false })
const touched = defineModel<boolean>('touched', { default: false })

const emit = defineEmits(['edit'])

const { status, error } = useItemImagesValidity(images, touched)

const stop = watchEffect(() => {
  valid.value = unref(status) === 'success'
})

tryOnUnmounted(stop)
</script>

<template>
  <div
    class="ItemImagesInput"
    :class="{ error: status === 'error' }"
  >
    <WithDropdownMessage
      :status="status"
      :msg-error="error"
      :msg-placement="msgPlacement"
    >
      <ItemImagesGallery
        :item="{ images_names: images }"
        editable
        @edit="() => emit('edit')"
      />
    </WithDropdownMessage>
    <transition
      name="pop"
      mode="out-in"
      appear
    >
      <div
        v-if="images.length === 0 || uploadStatus === 'idle'"
        class="upload-status idle"
      />
      <div
        v-else-if="uploadStatus === 'pending'"
        class="upload-status pending"
      >
        <LoadingAnimation :small="true" />
        <div>Téléversement des images...</div>
      </div>
      <div
        v-else-if="uploadStatus === 'success'"
        class="upload-status success"
      >
        <Check
          :size="24"
          :stroke-width="2"
        />
        <div>Images téléversées</div>
      </div>
      <div
        v-else-if="uploadStatus === 'error'"
        class="upload-status error"
      >
        <OctagonAlert
          :size="24"
          :stroke-width="2"
        />
        <div>Échec du téléversément</div>
      </div>
    </transition>
  </div>
</template>

<style scoped lang="scss">
.ItemImagesInput {
  position: relative;

  &.error {
    .ItemImagesGallery {
      box-shadow: 0 0 2px $red-700;
    }
  }

  .upload-status {
    @include flex-row;
    gap: 0.5em;
    position: absolute;
    padding: 0 1em;
    height: 3em;
    right: 0;
    bottom: -3em;
    font-size: 1.2em;

    &.pending {
      color: $neutral-500;
    }

    &.success {
      color: $primary-600;
    }

    &.error {
      color: $red-800;
    }
  }
}
</style>
