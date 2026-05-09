from app.shared.enums import EnumWithMetadata


class ReportType(int, EnumWithMetadata):
    user = 1
    item = 2
    chat = 3
