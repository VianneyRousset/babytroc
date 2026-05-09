# Compatibility shim — import from domain-specific modules instead.
from app.shared.enums import EnumWithMetadata  # noqa: F401
from app.domains.chat.enums import ChatMessageType  # noqa: F401
from app.domains.loan.enums import LoanRequestState  # noqa: F401
from app.domains.report.enums import ReportType  # noqa: F401
from app.domains.item.enums import ItemQueryAvailability  # noqa: F401
