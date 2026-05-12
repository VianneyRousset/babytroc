<script setup lang="ts">
type InputType = "email" | "password" | "search" | "tel" | "text" | "url";

export type TextInputProps = {
	placeholder?: string;
	type?: InputType;
	autofocus?: boolean;
	tabindex?: number;
	status?: "idle" | "pending" | "success" | "error";
	disabled?: boolean;
	readonly?: boolean;
};

const model = defineModel<string>();
const emit = defineEmits(["blur"]);

const props = withDefaults(defineProps<TextInputProps>(), {
	status: "idle",
	disabled: false,
	readonly: false,
});

const inputElement = useTemplateRef<HTMLElement>("input");

watch(inputElement, (_el) =>
	_el && props.autofocus ? _el.focus() : undefined,
);

const showPassword = ref<boolean>(false);

// monitor icons container width to add padding to input element
// thus avoiding overlaps
const { width: iconsWidth } = useElementSize(
	useTemplateRef<HTMLElement>("icons"),
	undefined,
	{ box: "border-box" },
);

const _type = computed(() => {
	if (props.type === "password")
		return unref(showPassword) ? "text" : "password";
	return props.type;
});
</script>

<template>
  <div class="TextInput">
    <input
      ref="input"
      v-model.trim="model"
      :size="1"
      :placeholder="props.placeholder"
      :type="type"
      :disabled="props.disabled"
      :readonly="props.readonly"
      :tabindex="props.tabindex"
      :autofocus="props.autofocus"
      :class="[status]"
      @blur="emit('blur')"
    >
    <div
      ref="icons"
      class="icons-wrapper"
    >
      <transition
        name="pop"
        mode="out-in"
        appear
      >
        <LoadingAnimation
          v-if="status === 'pending'"
          :small="true"
        />
        <TriangleAlert
          v-else-if="status === 'error'"
          class="error"
          :size="28"
          :stroke-width="1.5"
        />
        <Check
          v-else-if="status === 'success'"
          class="success"
          :size="28"
          :stroke-width="1.5"
        />
      </transition>
      <transition
        name="pop"
        mode="out-in"
      >
        <Eye
          v-if="props.type === 'password' && !showPassword"
          class="visibility"
          :size="28"
          :stroke-width="1.5"
          @click="showPassword = true"
        />
        <EyeOff
          v-else-if="props.type === 'password'"
          class="visibility"
          :size="28"
          :stroke-width="1.5"
          @click="showPassword = false"
        />
      </transition>
    </div>
  </div>
</template>

<style scoped lang="scss">
.TextInput {
  @include flex-row;
  position: relative;

  input {
    flex: 1;
    font-size: 1rem;
    height: 48px;
    box-sizing: border-box;
    border: 1px solid $border-default;
    border-radius: $radius-sm;
    padding: 0 $space-4;
    transition: border-color 200ms ease-out;

    padding-right: v-bind("`max(0.6em, calc(${iconsWidth}px + 12px))`");

    &:focus {
      border-color: $text-primary;
    }

    &:disabled {
      background: $bg-page;
      color: $text-tertiary;
    }

    &:read-only {
      background: $bg-page;
      color: $text-secondary;
      cursor: default;
    }

    &.error {
      border-color: $red-600;
    }
  }

  .icons-wrapper {
    @include flex-row;
    gap: $space-2;
    position: absolute;
    right: $space-3;
    color: $text-secondary;

    .LoadingAnimation {
      width: 24px;
    }

    .visibility {
      cursor: pointer;
    }

    .error {
      color: $red-600;
    }

    .success {
      color: $primary-text-safe;
    }
  }
}
</style>
