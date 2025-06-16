__all__ = ("Base", "Dish", "Tag", "dishes_tags", "User")

from .base import Base
from models.dish import Dish, Tag, dishes_tags
from models.user import User
