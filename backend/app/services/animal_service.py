"""
AnimalService — business logic for animal CRUD operations.
"""

from app.repositories.base import AnimalRepository
from app.services.animal_validation import validate_animal_data


class ValidationError(Exception):
    """Raised when incoming data fails validation rules."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class AnimalNotFoundError(Exception):
    """Raised when a requested animal does not exist or is not owned by the user."""

    def __init__(self, animal_id):
        self.animal_id = animal_id
        super().__init__(f"Animal with id {animal_id} not found.")


class AnimalService:
    """Encapsulates all animal-related business logic."""

    def __init__(self, repository: AnimalRepository):
        self._repo = repository

    # ---- Create ---------------------------------------------------------

    def create(self, data: dict, user_id) -> dict:
        errors = validate_animal_data(data)

        if errors:
            raise ValidationError(errors)

        # Never trust user_id coming from the client.
        # Always use the authenticated user's ID.
        animal_data = dict(data)
        animal_data["user_id"] = user_id

        return self._repo.create(animal_data)

    # ---- Read -----------------------------------------------------------

    def get_all(self, user_id=None) -> list[dict]:
        return self._repo.get_all(user_id=user_id)

    def get_by_id(self, animal_id, user_id) -> dict:
        record = self._repo.get_by_id(animal_id, user_id=user_id)

        if record is None:
            raise AnimalNotFoundError(animal_id)

        return record

    # ---- Update ---------------------------------------------------------

    def update(self, animal_id, data: dict, user_id) -> dict:
        errors = validate_animal_data(data, partial=True)

        if errors:
            raise ValidationError(errors)

        # Check that this animal belongs to the logged-in user.
        if self._repo.get_by_id(animal_id, user_id=user_id) is None:
            raise AnimalNotFoundError(animal_id)

        # Never allow the client to change ownership.
        update_data = dict(data)
        update_data.pop("user_id", None)

        return self._repo.update(
            animal_id,
            update_data,
            user_id=user_id
        )

    # ---- Delete ---------------------------------------------------------

    def delete(self, animal_id, user_id) -> bool:
        if not self._repo.delete(animal_id, user_id=user_id):
            raise AnimalNotFoundError(animal_id)

        return True