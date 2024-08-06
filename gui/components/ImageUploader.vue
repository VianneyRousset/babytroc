<script setup lang="ts">
const frame = true;
let dragover = ref(false);
</script>

<template>
  <div
    v-bind:class="{ frame, dragover }"
    @dragover="dragover = true"
    @dragleave="dragover = false"
  >
    <img src="/img/image.svg" />
    <label for="image-selector">Select image </label>
    <input id="image-selector" type="file" />
  </div>
</template>

<style scoped>
.frame {
  border: 1px solid #7f7878;
  border-radius: 0.4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  opacity: 50%;
  transition: opacity 0.1s ease;
}

.frame.dragover {
  opacity: 100%;
}

.frame.dragover img {
  transform: scale(1.1);
}

img {
  width: 60%;
  height: 50%;
  max-width: 128px;
  margin-bottom: 2rem;
  transition: transform 0.1s ease;
}

input {
  display: none;
}

label {
  color: #7f7878;
  border: 1px solid #7f7878;
  border-radius: 4px;
  background: transparent;
  padding: 6px 16px;
  cursor: pointer;
  opacity: 50%;
}

label:hover {
  opacity: 100%;
}

label:active {
  background: rgba(0, 0, 0, 0.1);
}

#box {
  color: white;
  display: flex;
  justify-content: center;
  height: 50vh;
  min-height: 38em;
  background: url("/img/login-box.svg") no-repeat center center;
  background-size: 38em;
}

#box > div {
  display: flex;
  flex-direction: column;
  margin-left: 0.5em;
  width: 20em;
  margin-top: 7em;
}

h1 {
  font-weight: normal;
  font-size: 2em;
  text-align: center;
  color: white;
  margin-bottom: 1.8em;
}

a {
  margin-top: 0.5em;
}

p {
  float: right;
  margin-right: 1.5em;
  color: #e7e7e6ff;
}

p.login-error {
  color: #6b240c;
  text-align: center;
}

@media only screen and (max-width: 800px) {
  #box > div {
    margin-left: 0em;
  }
}

.tooltip-container {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: all 0.3s;
  border-radius: 12px;
  cursor: pointer;
}

.tooltip {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.3em 0.6em;
  opacity: 0;
  pointer-events: none;
  transition: all 0.3s;
  background: #fcf5ed;
  border-radius: 12px;
  color: #df826c;
}

.tooltip::before {
  position: absolute;
  content: "";
  height: 0.6em;
  width: 0.6em;
  bottom: -0.2em;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  background: #fcf5ed;
}

.tooltip-container[active] .tooltip {
  top: -55%;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}
</style>
