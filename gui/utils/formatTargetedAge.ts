function formatTargetedAge(ageMin: number | null, ageMax: number | null): string {

  if (ageMin !== null && ageMin > 0) {

    if (ageMax === null)
      return `À partie de ${ageMin} mois`;

    return `De ${ageMin} à ${ageMax} mois`
  }

  if (ageMax !== null)
    return `Jusqu'à ${ageMax} mois`

  return "Pour tous âges"
}

export { formatTargetedAge };
