<script setup>
const model = defineModel();
const input = ref(null);

function focus() {
  input.value.focus();
}

defineExpose({ focus });

defineEmits(["submit"]);

defineProps({
  placeholder: {
    type: String,
    default: "",
  },
  type: {
    type: String,
    default: "text",
  },
});
</script>

<template>
  <div>
    <input
      ref="input"
      class="big"
      v-model="model"
      :placeholder="placeholder"
      :type="type"
      @keyup.enter="$emit('submit')"
    />
    <button @click="$emit('submit')">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="28"
        height="28"
        viewBox="0 0 22 22"
        stroke-width="2"
        stroke="white"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
        <path d="M5 12l14 0"></path>
        <path d="M13 18l6 -6"></path>
        <path d="M13 6l6 6"></path>
      </svg>
    </button>
  </div>
</template>

<style scoped>
div {
  position: relative;
  display: flex;
  border-radius: 50px;
  width: 100%;
}

button {
  background: #bfdeff;
  opacity: 50%;
  border-radius: 50px;
  border: none;
  aspect-ratio: 1;
  height: 80%;
  position: absolute;
  top: 10%;
  right: 5px;
  cursor: pointer;
}

button:hover {
  opacity: 100%;
}

button:active {
  background: #6e9eb6;
}
</style>
