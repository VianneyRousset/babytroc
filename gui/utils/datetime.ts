import { DateTime } from "luxon";

export function formatTargetedAge(
	ageMin: number | null,
	ageMax: number | null,
): string {
	if (ageMin !== null && ageMin > 0) {
		if (ageMax === null) return `À partie de ${ageMin} mois`;

		return `De ${ageMin} à ${ageMax} mois`;
	}

	if (ageMax !== null) return `Jusqu'à ${ageMax} mois`;

	return "Pour tous âges";
}

export function range2string(range: Array<number | null>): string {
	return `${range[0] ?? ""}-${range[1] ?? ""}`;
}

export function string2range(range: string): Array<number | null> {
	const { 0: min, 1: max } = { ...range.split("-") };
	return [
		min.length > 0 ? Number.parseInt(min) : null,
		max.length > 0 ? Number.parseInt(max) : null,
	];
}

export function ensureDateTime(datetime: DateTime | string): DateTime;
export function ensureDateTime(
	datetime: DateTime | string | null,
): DateTime | null;
export function ensureDateTime(
	datetime: DateTime | string | null,
): DateTime | null {
	if (datetime === null) return null;

	if (typeof datetime === "string")
		return DateTime.fromISO(datetime).setLocale("fr-CH");

	return datetime;
}

export function formatRelativeDate(datetime: DateTime | string): string {
	datetime = ensureDateTime(datetime);

	const now = DateTime.local().setLocale("fr-CH");

	if (datetime.hasSame(now, "day")) return "Aujourd'hui";

	if (datetime.hasSame(now.minus({ days: 1 }), "day")) return "Hier";

	if (datetime.hasSame(now, "year"))
		return datetime.toLocaleString({ month: "long", day: "numeric" });

	return datetime.toFormat("DDD");
}

export function formatRelativeDateRange(
	dateRange: [DateTime | string | null, DateTime | string | null],
): string {
	const start = ensureDateTime(dateRange[0]);
	const end = ensureDateTime(dateRange[1]);

	const now = DateTime.local().setLocale("fr-CH");

	if (start !== null) {
		// both start and end are finite
		if (end !== null) {
			if (start > end) throw new Error("Unsorted date range");

			// same start and end date
			if (start.hasSame(end, "day")) {
				if (start.hasSame(now, "day")) return "Aujourd'hui";

				if (start.hasSame(now.minus({ days: 1 }), "day")) return "Hier";

				if (start.hasSame(now, "year"))
					return `Le ${start.toLocaleString({ month: "long", day: "numeric" })}`;

				return `Le ${start.toFormat("DDD")}`;
			}

			// same start and end month
			if (start.hasSame(now, "month")) {
				if (start.hasSame(now, "year")) {
					return `Du ${start.toFormat("d")} au ${end.toFormat("d")} ${end.toFormat("MMMM")}`;
				} else {
					return `Du ${start.toFormat("d")} au ${end.toFormat("d")} ${end.toFormat("MMMM yyyy")}`;
				}
			}

			// same start and end year
			if (start.hasSame(now, "year")) {
				if (start.hasSame(now, "year")) {
					return `Du ${start.toFormat("d")} au ${end.toFormat("d")} ${end.toFormat("MMMM")}`;
				} else {
					return `Du ${start.toFormat("d")} au ${end.toFormat("d")} ${end.toFormat("MMMM yyyy")}`;
				}
			}

			return `Du ${start.toFormat("DDD")} au ${end.toFormat("DDD")}`;
		} else {
			// no end date

			if (start.hasSame(now, "day")) return "Depuis aujourd'hui";

			if (start.hasSame(now.minus({ days: 1 }), "day")) return "Depuis hier";

			if (start.hasSame(now, "year"))
				return `Depuis le ${start.toLocaleString({ month: "long", day: "numeric" })}`;

			return `Depuis le ${start.toFormat("DDD")}`;
		}
	} else {
		// no start date

		// with end date
		if (end !== null) {
			if (end.hasSame(now, "day")) return "Jusqu'à aujourd'hui";

			if (end.hasSame(now.minus({ days: 1 }), "day")) return "Jusqu'a hier";

			if (end.hasSame(now, "year"))
				return `Jusqu'au ${end.toLocaleString({ month: "long", day: "numeric" })}`;

			return `Jusqu'au ${end.toFormat("DDD")}`;
		} else {
			return "Jamais";
		}
	}
}
