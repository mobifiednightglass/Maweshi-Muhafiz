"""
AnimalService — business logic for animal CRUD operations.

Receives an AnimalRepository via constructor injection so the storage
backend can be swapped (in-memory → MongoDB) without touching this code.
"""
#This file is handling the business logic for the animal CRUD operations
from app.repositories.base import AnimalRepository
from app.services.animal_validation import validate_animal_data


# ---------------------------------------------------------------------------
# Custom exceptions — routes catch these and map to HTTP status codes
# ---------------------------------------------------------------------------

class ValidationError(Exception):
    """Raised when incoming data fails validation rules."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class AnimalNotFoundError(Exception):
    """Raised when a requested animal id does not exist."""

    def __init__(self, animal_id):
        self.animal_id = animal_id
        super().__init__(f"Animal with id {animal_id} not found.")


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class AnimalService:
    """Encapsulates all animal-related business logic."""

    def __init__(self, repository: AnimalRepository):
        self._repo = repository

    # ---- Create ---------------------------------------------------------

    def create(self, data: dict) -> dict:
        errors = validate_animal_data(data)
        if errors:
            raise ValidationError(errors)
        return self._repo.create(data)

    # ---- Read -----------------------------------------------------------

    def get_all(self) -> list[dict]:
        return self._repo.get_all()

    def get_by_id(self, animal_id) -> dict:
        record = self._repo.get_by_id(animal_id)
        if record is None:
            raise AnimalNotFoundError(animal_id)
        return record

    # ---- Update ---------------------------------------------------------

    def update(self, animal_id, data: dict) -> dict:
        # Validate only the fields that are present (partial update)
        errors = validate_animal_data(data, partial=True)
        if errors:
            raise ValidationError(errors)

        # Check existence before delegating to the repository
        if self._repo.get_by_id(animal_id) is None:
            raise AnimalNotFoundError(animal_id)

        return self._repo.update(animal_id, data)

    # ---- Delete ---------------------------------------------------------

    def delete(self, animal_id) -> bool:
        if not self._repo.delete(animal_id):
            raise AnimalNotFoundError(animal_id)
        return True
