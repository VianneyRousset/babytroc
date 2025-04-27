import { defaults } from "lodash";

// assign properties of `source` to `target`
// if `remove` is true, properties of `target` that are not defined in `target` are removed
function assign<T extends {}>(
	target: T,
	source: T,
	options?: { remove?: boolean },
): T {
	// default options
	const _options = defaults(options ?? {}, {
		remove: false,
	});

	// remove properties
	if (_options.remove) {
		for (const key of new Set(Object.keys(target)).difference(
			new Set(Object.keys(source)),
		)) {
			delete target[key as keyof T];
		}
	}

	return Object.assign(target, source);
}

export { assign };
