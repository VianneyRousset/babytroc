from babytroc.shared.enums import EnumWithMetadata


class ModerationReportType(int, EnumWithMetadata):
    user = 1
    item = 2
    chat = 3
