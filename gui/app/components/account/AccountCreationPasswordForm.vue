<script setup lang="ts">
import { OctagonAlert } from "lucide-vue-next";

const props = defineProps<{
	loading?: boolean;
	disabled?: boolean;
	apiUrl: string;
	siteKey: string;
}>();

const { loading, disabled, apiUrl, siteKey } = toRefs(props);

const password = defineModel<string>("password", { default: "" });
const valid = defineModel<boolean>("valid");
const capToken = defineModel<string>("capToken", { default: "" });
const website = defineModel<string>("website", { default: "" });

const emit = defineEmits(["next"]);

const capConfigured = computed<boolean>(
	() => unref(apiUrl) !== "" && unref(siteKey) !== "",
);

const canSubmit = computed<boolean>(
	() =>
		unref(valid) === true &&
		unref(capToken) !== "" &&
		unref(website) === "" &&
		unref(capConfigured),
);

const resetSignal = ref(0);

function bumpResetSignal() {
	resetSignal.value += 1;
	capToken.value = "";
}

defineExpose({ bumpResetSignal });

const next = () => unref(canSubmit) && emit("next");
</script>

<template>
  <section class="AccountCreationPasswordForm">

    <Honeypot v-model="website" />

    <CapWidget
      v-if="capConfigured"
      :api-url="apiUrl"
      :site-key="siteKey"
      :reset-signal="resetSignal"
      :disabled="loading"
      @solve="capToken = $event"
      @expire="capToken = ''"
    />
    <PanelBanner
      v-else
      color="red"
      :icon="OctagonAlert"
    >
      Captcha indisponible.
    </PanelBanner>

    <AccountPasswordInput
      v-model:password="password"
      v-model:valid="valid"
      msg-placement="top"
      :tabindex="0"
      :disabled="loading || disabled"
      autofocus
      @next="next"
    />

    <TextButton
      aspect="flat"
      size="large"
      color="primary"
      :loading="loading"
      :disabled="!canSubmit || loading || disabled"
      @click="next"
    >
      Créer un compte
    </TextButton>
  </section>
</template>

<style scoped lang="scss">
.AccountCreationPasswordForm {
  @include flex-column;
  align-items: stretch;
  gap: 1em;
}

.CapWidget {
  margin-bottom: 2em;
}
</style>
