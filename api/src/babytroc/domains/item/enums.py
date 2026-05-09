from babytroc.shared.enums import EnumWithMetadata


class ItemQueryAvailability(str, EnumWithMetadata):
    yes = "y"
    no = "n"
    all = "a"
