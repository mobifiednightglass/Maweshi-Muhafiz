"""Repositories package — data-access abstraction layer."""

from app.repositories.base import AnimalRepository, UserRepository
from app.repositories.in_memory import InMemoryAnimalRepository
from app.repositories.in_memory_user import InMemoryUserRepository
from app.repositories.mongo import MongoAnimalRepository
from app.repositories.mongo_user import MongoUserRepository

__all__ = [
    "AnimalRepository",
    "UserRepository",
    "InMemoryAnimalRepository",
    "InMemoryUserRepository",
    "MongoAnimalRepository",
    "MongoUserRepository",
]
