/**
 * Volar plugin: tell the Vue template type-checker to treat <cap-widget>
 * as a native custom element instead of resolving it to the <CapWidget>
 * Vue component registered in GlobalComponents.
 */

/** @type {import('@vue/language-core').VueLanguagePlugin} */
const plugin = () => ({
	version: 2,
	name: "custom-elements",
	resolveTemplateCompilerOptions(options) {
		const upstream = options.isCustomElement;
		return {
			...options,
			isCustomElement: (tag) =>
				tag === "cap-widget" || (upstream ? upstream(tag) : false),
		};
	},
});

module.exports = plugin;
