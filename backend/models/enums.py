import enum


class RoleEnum(str, enum.Enum):
    employee = "employee"
    agent = "agent"


class PriorityEnum(str, enum.Enum):
    low = "Low"
    medium = "Medium"
    high = "High"
    critical = "Critical"


class CategoryEnum(str, enum.Enum):
    hardware = "Hardware"
    software = "Software"
    network = "Network"
    access = "Access"


class StatusEnum(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"