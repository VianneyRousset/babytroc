
function formatMonthRange(range: Array<number | null>): string {
  return `${range[0] ?? ""}-${range[1] ?? ""}`;
}

function parseMonthRange(range: string): Array<number | null> {
  const { 0: min, 1: max } = { ...(range.split("-")) };
  return [
    min.length > 0 ? Number(min) : null,
    max.length > 0 ? Number(max) : null,
  ]
}


export { formatMonthRange, parseMonthRange };
