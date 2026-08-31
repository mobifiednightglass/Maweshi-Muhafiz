"""Repositories package — data-access abstraction layer."""

from app.repositories.base import (
    AnimalRepository,
    HealthAssessmentRepository,
    UserRepository,
    VetCaseSummaryRepository,
)
from app.repositories.in_memory import InMemoryAnimalRepository
from app.repositories.in_memory_user import InMemoryUserRepository
from app.repositories.in_memory_vet_summary import InMemoryVetCaseSummaryRepository
from app.repositories.mongo import MongoAnimalRepository
from app.repositories.mongo_health import MongoHealthAssessmentRepository
from app.repositories.mongo_user import MongoUserRepository
from app.repositories.mongo_vet_summary import MongoVetCaseSummaryRepository

__all__ = [
    "AnimalRepository",
    "HealthAssessmentRepository",
    "UserRepository",
    "VetCaseSummaryRepository",
    "InMemoryAnimalRepository",
    "InMemoryUserRepository",
    "InMemoryVetCaseSummaryRepository",
    "MongoAnimalRepository",
    "MongoHealthAssessmentRepository",
    "MongoUserRepository",
    "MongoVetCaseSummaryRepository",
]
