<script setup lang="ts">
const props = defineProps<{
  small?: boolean
}>()

const { small } = toRefs(props)
</script>

<template>
  <div
    v-if="small"
    class="spinner-small"
  >
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
    <div class="spinner-small-blade" />
  </div>
  <div
    v-else
    class="spinner-big"
  >
    <div />
  </div>
</template>

<style lang="scss" scoped>
.spinner-big {
  @include flex-row-center;
  width: 48px;
  height: 48px;

  &>div {
    border: 4px solid rgba(0, 0, 0, .1);
    border-left-color: transparent;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    animation: spin89345 1s linear infinite;
  }
}

@keyframes spin89345 {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.spinner-small {
  font-size: 24px;
  position: relative;
  display: inline-block;
  width: 1em;
  height: 1em;
}

.spinner-small .spinner-small-blade {
  position: absolute;
  left: 0.4629em;
  bottom: 0;
  width: 0.074em;
  height: 0.2777em;
  border-radius: 0.0555em;
  background-color: transparent;
  -webkit-transform-origin: center -0.2222em;
  -ms-transform-origin: center -0.2222em;
  transform-origin: center -0.2222em;
  animation: spinner-small-fade9234 1s infinite linear;
}

.spinner-small .spinner-small-blade:nth-child(1) {
  -webkit-animation-delay: 0s;
  animation-delay: 0s;
  -webkit-transform: rotate(0deg);
  -ms-transform: rotate(0deg);
  transform: rotate(0deg);
}

.spinner-small .spinner-small-blade:nth-child(2) {
  -webkit-animation-delay: 0.083s;
  animation-delay: 0.083s;
  -webkit-transform: rotate(30deg);
  -ms-transform: rotate(30deg);
  transform: rotate(30deg);
}

.spinner-small .spinner-small-blade:nth-child(3) {
  -webkit-animation-delay: 0.166s;
  animation-delay: 0.166s;
  -webkit-transform: rotate(60deg);
  -ms-transform: rotate(60deg);
  transform: rotate(60deg);
}

.spinner-small .spinner-small-blade:nth-child(4) {
  -webkit-animation-delay: 0.249s;
  animation-delay: 0.249s;
  -webkit-transform: rotate(90deg);
  -ms-transform: rotate(90deg);
  transform: rotate(90deg);
}

.spinner-small .spinner-small-blade:nth-child(5) {
  -webkit-animation-delay: 0.332s;
  animation-delay: 0.332s;
  -webkit-transform: rotate(120deg);
  -ms-transform: rotate(120deg);
  transform: rotate(120deg);
}

.spinner-small .spinner-small-blade:nth-child(6) {
  -webkit-animation-delay: 0.415s;
  animation-delay: 0.415s;
  -webkit-transform: rotate(150deg);
  -ms-transform: rotate(150deg);
  transform: rotate(150deg);
}

.spinner-small .spinner-small-blade:nth-child(7) {
  -webkit-animation-delay: 0.498s;
  animation-delay: 0.498s;
  -webkit-transform: rotate(180deg);
  -ms-transform: rotate(180deg);
  transform: rotate(180deg);
}

.spinner-small .spinner-small-blade:nth-child(8) {
  -webkit-animation-delay: 0.581s;
  animation-delay: 0.581s;
  -webkit-transform: rotate(210deg);
  -ms-transform: rotate(210deg);
  transform: rotate(210deg);
}

.spinner-small .spinner-small-blade:nth-child(9) {
  -webkit-animation-delay: 0.664s;
  animation-delay: 0.664s;
  -webkit-transform: rotate(240deg);
  -ms-transform: rotate(240deg);
  transform: rotate(240deg);
}

.spinner-small .spinner-small-blade:nth-child(10) {
  -webkit-animation-delay: 0.747s;
  animation-delay: 0.747s;
  -webkit-transform: rotate(270deg);
  -ms-transform: rotate(270deg);
  transform: rotate(270deg);
}

.spinner-small .spinner-small-blade:nth-child(11) {
  -webkit-animation-delay: 0.83s;
  animation-delay: 0.83s;
  -webkit-transform: rotate(300deg);
  -ms-transform: rotate(300deg);
  transform: rotate(300deg);
}

.spinner-small .spinner-small-blade:nth-child(12) {
  -webkit-animation-delay: 0.913s;
  animation-delay: 0.913s;
  -webkit-transform: rotate(330deg);
  -ms-transform: rotate(330deg);
  transform: rotate(330deg);
}

@keyframes spinner-small-fade9234 {
  0% {
    background-color: var(--loader-color);
  }

  100% {
    background-color: transparent;
  }
}
</style>
