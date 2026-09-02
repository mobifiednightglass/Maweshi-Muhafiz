"""Repositories package — data-access abstraction layer."""

from app.repositories.base import (
    AnimalRepository,
    HealthAssessmentRepository,
    ReminderRepository,
    UserRepository,
    VetCaseSummaryRepository,
)
from app.repositories.in_memory import InMemoryAnimalRepository
from app.repositories.in_memory_reminders import InMemoryReminderRepository
from app.repositories.in_memory_user import InMemoryUserRepository
from app.repositories.in_memory_vet_summary import InMemoryVetCaseSummaryRepository
from app.repositories.mongo import MongoAnimalRepository
from app.repositories.mongo_health import MongoHealthAssessmentRepository
from app.repositories.mongo_reminders import MongoReminderRepository
from app.repositories.mongo_user import MongoUserRepository
from app.repositories.mongo_vet_summary import MongoVetCaseSummaryRepository

__all__ = [
    "AnimalRepository",
    "HealthAssessmentRepository",
    "ReminderRepository",
    "UserRepository",
    "VetCaseSummaryRepository",
    "InMemoryAnimalRepository",
    "InMemoryReminderRepository",
    "InMemoryUserRepository",
    "InMemoryVetCaseSummaryRepository",
    "MongoAnimalRepository",
    "MongoHealthAssessmentRepository",
    "MongoReminderRepository",
    "MongoUserRepository",
    "MongoVetCaseSummaryRepository",
]
