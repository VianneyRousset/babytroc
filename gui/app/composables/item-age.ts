export function useItemTargetedAgeMonths<T extends { targeted_age_months: string }>(
  item: MaybeRefOrGetter<T>,
): {
  targetedAgeMonths: Ref<AgeRange>
  formatedTargetedAgeMonths: Ref<string>
} {
  const targetedAgeMonths = computed(() => string2range(toValue(item).targeted_age_months))
  const formatedTargetedAgeMonths = computed(() => {
    return formatTargetedAge(...unref(targetedAgeMonths))
  })

  return { targetedAgeMonths, formatedTargetedAgeMonths }
}
