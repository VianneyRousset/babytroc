import { defaults } from "lodash";

// assign properties of `source` to `target`
// if `remove` is true, properties of `target` that are not defined in `target` are removed
function assign<T extends Object>(
	target: T,
	source: T,
	options?: { remove?: boolean },
): T {
	// default options
	options = defaults(options ?? {}, {
		remove: false,
	});

	// remove properties
	if (options.remove)
		new Set(Object.keys(target))
			.difference(new Set(Object.keys(source)))
			.forEach((key) => delete target[key as keyof T]);

	return Object.assign(target, source);
}

export { assign };
