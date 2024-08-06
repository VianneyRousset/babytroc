<script setup lang="ts">

const props = defineProps({
  state: {
    type: String,
    required: false,
  },
  errormsg: {
    type: String,
    required: false,
  },
});


const dragOver = ref(0);
dragOver.value = false;
const emit = defineEmits(["new-files"]);

function dragEnter(event) {
  event.preventDefault();
  event.stopPropagation();
  dragOver.value = true;
}

function dragLeave(event) {
  event.preventDefault();
  event.stopPropagation();
  dragOver.value = false;
}

function drop(event) {
  dragOver.value = false;
  if (event.dataTransfer.files.length) {
    emit("new-files", event.dataTransfer.files);
  }
}

function select(event) {
  if (event.target.files.length) {
    emit("new-files", event.target.files);
  }
}

</script>

<template>
  <div :class="{ box: true, dragover: dragOver }" @dragenter.prevent="dragEnter" @dragleave.prevent="dragLeave"
    @drop.prevent="drop" @dragover.prevent>
    <div class="panel error" v-if="props.state == 'error'">
      <div>
        <strong>Error</strong>
      </div>
      <div>
        {{ props.errormsg }}
      </div>
    </div>
    <div v-if="props.state != 'loading'" class="input">
      <input type="file" id="file" accept="image/*" @change="select" />
      <label for="file"><strong>Sélectionner un fichier</strong><span> ou le glisser ici</span>.</label>
    </div>
    <div class="panel loading" v-if="props.state == 'loading'">
      <Loader />
    </div>
    <div class="panel success" v-if="props.state == 'success'">Done!</div>
  </div>
</template>

<style scoped>
input[type="file"] {
  width: 0.1px;
  height: 0.1px;
  opacity: 0;
  overflow: hidden;
  position: absolute;
  z-index: -1;
}

label {
  cursor: pointer;
  color: var(--brand-600);
}

.panel {
  color: var(--brand-600);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.box {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  justify-content: center;
  align-items: center;
  background: var(--brand-50);
  outline: 2px dashed var(--brand-300);
  outline-offset: -2rem;
  flex-grow: 1;
}

.box.dragover {
  background: var(--brand-100);
}
</style>
