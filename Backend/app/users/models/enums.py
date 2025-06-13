from enum import Enum

class UserType(Enum):
    ADMIN = 'admin'
    MANAGER = 'manager'
    REGULAR_USER = 'regular_user'