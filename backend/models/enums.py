import enum


class RoleEnum(str, enum.Enum):
    employee = "employee"
    admin = "admin"


class CategoryEnum(str, enum.Enum):
    email = "email"
    network = "network"
    hardware = "hardware"
    software = "software"
    other = "other"


class StatusEnum(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"
