export const useItemNameValidity = defineValidityFunction<string>((_name) => {
  // validity pattern (unicode letters with ' ' and '-' not at the ends)
  const validCharactersRegex = /^\p{L}[\p{L} \-']+\p{L}$/u

  if (_name === '') return 'Veuillez spécifier un nom'
  if (_name.length < 5) return 'Nom trop court'
  if (_name.length > 30) return 'Nom trop long'
  if (!validCharactersRegex.test(_name)) return 'Nom invalide'
  return undefined
}, {
  initialValue: '',
})

export const useItemDescriptionValidity = defineValidityFunction<string>((_description) => {
  if (_description === '') return 'Veuillez spécifier une description'
  if (_description.length < 20) return 'Description trop courte'
  if (_description.length > 600) return 'Description trop longue'
  return undefined
}, {
  initialValue: '',
})

export const useItemRegionsValidity = defineValidityFunction<Set<number>>(
  _regions => (_regions.size < 1) ? 'Veuillez spécifier au moins une région' : undefined,
  {
    initialValue: new Set(),
    compare: (a: Set<number>, b: Set<number>) => a.size === b.size && [...a].every(x => b.has(x)),
  },
)

export const useItemImagesValidity = defineValidityFunction<Array<string>>(
  _images => (_images.length < 1) ? 'Veuillez spécifier au moins une image' : undefined,
  {
    initialValue: [],
    compare: (a: Array<string>, b: Array<string>) => a.length === b.length && a.every((el, i) => b[i] === el),
  },
)
