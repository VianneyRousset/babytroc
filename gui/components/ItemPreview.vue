<script setup>

// TODO "missing image" if item.image is missing

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
  "clickable": {
    type: Boolean,
    required: false,
  },
  "show-info": {
    type: Boolean,
    required: false,
  },
  "image-size": {
    type: String,
    required: false,
  },
  "statuses": {
    type: Object,
    required: false,
  }
});

const emit = defineEmits(["select"]);

const backgroundImage = ref("");

// update backgroundImage when props change
watch(() => [props.item, props.showInfo, props.imageSize], ([newItemValue, newShowInfoValue, newImageSizeValue]) => {

  const backgrounds = []
  var params = "";

  if (newShowInfoValue) {
    backgrounds.push("linear-gradient(transparent 0 50%, var(--neutral-950) 100%)");
  }

  if (newImageSizeValue !== undefined) {
    params = `?w=${newImageSizeValue}&h=${newImageSizeValue}`;
  }

  backgrounds.push(`url('/api/images/${newItemValue.image}${params}')`);

  backgroundImage.value = backgrounds.join(", ");

}, { immediate: true });

</script>

<template>
  <div :class="{ box: true, clickable: clickable }" @click="emit('select');"
    :style="{ backgroundImage: backgroundImage, }">
    <div class="status">

      <!-- ok -->
      <svg v-if="props?.statuses?.ok" class="status-icon ok" xmlns="http://www.w3.org/2000/svg" viewBox="-12 -12 48 48"
        width="64" height="64">
        <path
          d="M1 12C1 5.925 5.925 1 12 1s11 4.925 11 11-4.925 11-11 11S1 18.075 1 12Zm16.28-2.72a.751.751 0 0 0-.018-1.042.751.751 0 0 0-1.042-.018l-5.97 5.97-2.47-2.47a.751.751 0 0 0-1.042.018.751.751 0 0 0-.018 1.042l3 3a.75.75 0 0 0 1.06 0Z">
        </path>
      </svg>

      <!-- nok -->
      <svg v-if="props?.statuses?.nok" class="status-icon nok" xmlns="http://www.w3.org/2000/svg"
        viewBox="-12 -12 48 48" width="64" height="64">
        <path
          d="M1 12C1 5.925 5.925 1 12 1s11 4.925 11 11-4.925 11-11 11S1 18.075 1 12Zm8.036-4.024a.751.751 0 0 0-1.042.018.751.751 0 0 0-.018 1.042L10.939 12l-2.963 2.963a.749.749 0 0 0 .326 1.275.749.749 0 0 0 .734-.215L12 13.06l2.963 2.964a.75.75 0 0 0 1.061-1.06L13.061 12l2.963-2.964a.749.749 0 0 0-.326-1.275.749.749 0 0 0-.734.215L12 10.939Z">
        </path>
      </svg>

      <!-- tag -->
      <svg v-if="props?.statuses?.tag" class="status-icon tag" xmlns="http://www.w3.org/2000/svg"
        viewBox="-12 -12 48 48" width="64" height="64">
        <path
          d="M 2.5 1 C 1.6715737 1 1 1.6715737 1 2.5 L 1 10.939453 C 1.0000201 11.33721 1.1577888 11.719153 1.4394531 12 L 11.689453 22.25 C 12.275088 22.834906 13.224912 22.834906 13.810547 22.25 L 22.25 13.810547 C 22.834906 13.224912 22.834906 12.275088 22.25 11.689453 L 12 1.4394531 C 11.718965 1.1580684 11.337144 1.0003501 10.939453 1 L 2.5 1 z M 7.75 6.5 A 1.25 1.25 0 0 1 7.75 9 A 1.25 1.25 0 0 1 7.75 6.5 z">
        </path>
      </svg>

      <!-- star -->
      <svg v-if="props?.statuses?.star" class="status-icon star" xmlns="http://www.w3.org/2000/svg"
        viewBox="-12 -12 48 48" width="64" height="64">
        <path
          d="m12.672.668 3.059 6.197 6.838.993a.75.75 0 0 1 .416 1.28l-4.948 4.823 1.168 6.812a.75.75 0 0 1-1.088.79L12 18.347l-6.116 3.216a.75.75 0 0 1-1.088-.791l1.168-6.811-4.948-4.823a.749.749 0 0 1 .416-1.279l6.838-.994L11.327.668a.75.75 0 0 1 1.345 0Z">
        </path>
      </svg>

    </div>
    <div class="info" v-if="props.showInfo">
      <div class="location">Montchoisi</div>
      <div class="name">{{ props.item.name }}</div>
    </div>
  </div>
</template>

<style scoped>
.status-icon {
  position: relative;
  top: -12px;
  right: -12px;
}

.status-icon.ok {
  fill: var(--brand-200);
}

.status-icon.nok {
  fill: #E76F51;
}

.status-icon.tag {
  fill: #96C9F4;
}

.status-icon.star {
  fill: #E9C46A;
}

svg.status-icon path {
  box-shadow: 0px 0px 20px black;
  filter: drop-shadow(0px 0px 4px rgb(0 0 0 / 0.9));
}

.box {
  display: flex;
  box-sizing: border-box;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 1rem;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
}

.box.clickable {
  cursor: pointer;
}

.box.clickable:hover {
  opacity: 90%;
}

.box:target {
  /* ensure the target element (anchor) is not flushed to the top */
  scroll-margin-top: 20vh;
  animation: flash;
  animation-duration: 0.8s;
}

.box>div {
  padding: 1rem;
}

.status {
  display: flex;
  justify-content: right;
}

.location {
  color: var(--brand-400);
  margin-bottom: 0.2em;
}

.name {
  font-family: "Plus Jakarta Sans", sans-serif;
  color: var(--brand-50);
  font-size: 2rem;
  font-weight: bold;
}

.name-status>img {
  width: clamp(2em, 10vw, 2.5em);
  margin-left: 1em;
}
</style>
