<script setup lang="ts">
const model = defineModel<Set<string>>({ default: () => new Set() });

const props = withDefaults(
	defineProps<{
		size?: "large" | "normal";
	}>(),
	{
		size: "normal",
	},
);

const { size } = toRefs(props);

const { categories, status } = useCategoriesList();
const { roots, childrenOf } = useCategoryTree(categories);

// Only one category can be expanded at a time
const expandedSlug = ref<string | null>(null);

function _toggleExpand(slug: string) {
	expandedSlug.value = unref(expandedSlug) === slug ? null : slug;
}

function parentState(parentSlug: string): "all" | "some" | "none" {
	const children = childrenOf(parentSlug);
	if (children.length === 0) {
		return model.value?.has(parentSlug) ? "all" : "none";
	}
	const selectedCount = children.filter((c) => model.value?.has(c.slug)).length;
	if (selectedCount === 0 && !model.value?.has(parentSlug)) return "none";
	if (selectedCount === children.length) return "all";
	return "some";
}

function _toggleParent(parentSlug: string) {
	const children = childrenOf(parentSlug);
	const next = new Set(model.value);
	const state = parentState(parentSlug);

	if (state === "all") {
		// Deselect all
		next.delete(parentSlug);
		for (const c of children) next.delete(c.slug);
	} else {
		// Select all
		next.add(parentSlug);
		for (const c of children) next.add(c.slug);
	}
	model.value = next;
}

function _toggleChild(parentSlug: string, childSlug: string) {
	const children = childrenOf(parentSlug);
	const next = new Set(model.value);

	if (next.has(childSlug)) {
		next.delete(childSlug);
		next.delete(parentSlug);
	} else {
		next.add(childSlug);
		// If all children now selected, also select parent
		if (children.every((c) => c.slug === childSlug || next.has(c.slug))) {
			next.add(parentSlug);
		}
	}
	model.value = next;
}
</script>

<template>
  <div
    v-if="status === 'success'"
    class="CategoriesCheckboxes"
  >
    <div
      v-for="root in roots"
      :key="root.slug"
      class="category-group"
    >
      <div class="parent-row">
        <Checkbox
          :model-value="parentState(root.slug) === 'all'"
          :indeterminate="parentState(root.slug) === 'some'"
          :size="size"
          @update:model-value="() => toggleParent(root.slug)"
        >
          {{ root.name }}
        </Checkbox>
        <button
          v-if="childrenOf(root.slug).length > 0"
          class="expand-toggle"
          :class="{ expanded: expandedSlug === root.slug }"
          @click="toggleExpand(root.slug)"
        >
          <ChevronDown
            :size="16"
            :stroke-width="2"
          />
        </button>
      </div>

      <div
        v-if="expandedSlug === root.slug && childrenOf(root.slug).length > 0"
        class="children"
      >
        <Checkbox
          v-for="child in childrenOf(root.slug)"
          :key="child.slug"
          :model-value="model?.has(child.slug) ?? false"
          :size="size"
          @update:model-value="() => toggleChild(root.slug, child.slug)"
        >
          {{ child.name }}
        </Checkbox>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.CategoriesCheckboxes {
  display: flex;
  flex-direction: column;
  gap: $space-1;

  .category-group {
    .parent-row {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .expand-toggle {
        @include reset-button;
        cursor: pointer;
        padding: $space-2;
        color: $text-tertiary;
        transition: transform 200ms ease-out;

        &.expanded {
          transform: rotate(180deg);
        }
      }
    }

    .children {
      display: flex;
      flex-direction: column;
      padding-left: $space-6;
      gap: $space-1;
    }
  }
}
</style>
