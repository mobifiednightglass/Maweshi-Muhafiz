"""
Tests for the InMemoryVetCaseSummaryRepository.

Covers:
  1. Creating a summary and retrieving it
  2. User-scoped access (cannot see another user's summary)
  3. Listing summaries by user
  4. Lookup by assessment_id
  5. Deletion (scoped to owner)
  6. Assessment data snapshot
  7. App factory wiring (vet_summary_repo available on app)
"""

import pytest

from app import create_app
from app.repositories.in_memory_vet_summary import InMemoryVetCaseSummaryRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def repo():
    return InMemoryVetCaseSummaryRepository()


@pytest.fixture
def sample_data():
    """Minimal valid data for creating a vet case summary."""
    return {
        "user_id": "user_1",
        "animal_id": "animal_42",
        "assessment_id": "assessment_7",
        "symptoms": "The animal is limping on the front left leg.",
        "image_ids": ["img_001"],
        "diagnosis_result": {
            "possible_conditions": ["Sprain", "Hoof injury"],
            "explanation": "Visible limp on front left leg.",
            "confidence_note": "AI-assisted preliminary assessment.",
            "urgency_level": "medium",
        },
        "status": "completed",
        "is_red_flag": False,
        "red_flag_reasons": [],
        "animal": {
            "id": "animal_42",
            "name": "Moti",
            "animal_type": "Cow",
            "breed": "Sahiwal",
            "gender": "Female",
            "age": 5,
            "weight": 350.0,
            "color": "Brown",
            "health_status": "healthy",
        },
    }


# ---------------------------------------------------------------------------
# 1. Create and retrieve
# ---------------------------------------------------------------------------

class TestCreate:
    def test_create_returns_dict_with_id(self, repo, sample_data):
        result = repo.create(sample_data)
        assert "id" in result
        assert result["id"] is not None

    def test_create_sets_created_at(self, repo, sample_data):
        result = repo.create(sample_data)
        assert "created_at" in result
        assert result["created_at"] is not None

    def test_create_stores_user_id(self, repo, sample_data):
        result = repo.create(sample_data)
        assert result["user_id"] == "user_1"

    def test_create_stores_animal_id(self, repo, sample_data):
        result = repo.create(sample_data)
        assert result["animal_id"] == "animal_42"

    def test_create_stores_assessment_id(self, repo, sample_data):
        result = repo.create(sample_data)
        assert result["assessment_id"] == "assessment_7"

    def test_auto_increment_ids(self, repo, sample_data):
        r1 = repo.create(sample_data)
        sample_data["assessment_id"] = "assessment_8"
        r2 = repo.create(sample_data)
        assert r2["id"] == r1["id"] + 1


# ---------------------------------------------------------------------------
# 2. Get by id (user-scoped)
# ---------------------------------------------------------------------------

class TestGetById:
    def test_get_existing_summary(self, repo, sample_data):
        created = repo.create(sample_data)
        fetched = repo.get_by_id(created["id"], user_id="user_1")
        assert fetched is not None
        assert fetched["id"] == created["id"]

    def test_get_nonexistent_returns_none(self, repo):
        assert repo.get_by_id(999, user_id="user_1") is None

    def test_get_wrong_user_returns_none(self, repo, sample_data):
        created = repo.create(sample_data)
        assert repo.get_by_id(created["id"], user_id="other_user") is None

    def test_get_invalid_id_returns_none(self, repo):
        assert repo.get_by_id("not-a-number", user_id="user_1") is None


# ---------------------------------------------------------------------------
# 3. Get by user_id
# ---------------------------------------------------------------------------

class TestGetByUserId:
    def test_empty_for_user_with_no_summaries(self, repo):
        assert repo.get_by_user_id("nobody") == []

    def test_returns_only_own_summaries(self, repo, sample_data):
        repo.create(sample_data)
        other = {**sample_data, "user_id": "user_2", "assessment_id": "a_99"}
        repo.create(other)

        user1_summaries = repo.get_by_user_id("user_1")
        assert len(user1_summaries) == 1
        assert user1_summaries[0]["user_id"] == "user_1"

        user2_summaries = repo.get_by_user_id("user_2")
        assert len(user2_summaries) == 1
        assert user2_summaries[0]["user_id"] == "user_2"

    def test_multiple_summaries_for_same_user(self, repo, sample_data):
        repo.create(sample_data)
        sample_data["assessment_id"] = "assessment_8"
        repo.create(sample_data)
        assert len(repo.get_by_user_id("user_1")) == 2


# ---------------------------------------------------------------------------
# 4. Get by assessment_id (user-scoped)
# ---------------------------------------------------------------------------

class TestGetByAssessmentId:
    def test_find_by_assessment_id(self, repo, sample_data):
        repo.create(sample_data)
        result = repo.get_by_assessment_id("assessment_7", user_id="user_1")
        assert result is not None
        assert result["assessment_id"] == "assessment_7"

    def test_wrong_user_returns_none(self, repo, sample_data):
        repo.create(sample_data)
        assert repo.get_by_assessment_id("assessment_7", user_id="other") is None

    def test_nonexistent_assessment_returns_none(self, repo):
        assert repo.get_by_assessment_id("no_such", user_id="user_1") is None


# ---------------------------------------------------------------------------
# 5. Delete (owner-scoped)
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_own_summary(self, repo, sample_data):
        created = repo.create(sample_data)
        assert repo.delete(created["id"], user_id="user_1") is True
        assert repo.get_by_id(created["id"], user_id="user_1") is None

    def test_delete_other_users_summary_fails(self, repo, sample_data):
        created = repo.create(sample_data)
        assert repo.delete(created["id"], user_id="other_user") is False
        # Original still exists
        assert repo.get_by_id(created["id"], user_id="user_1") is not None

    def test_delete_nonexistent_returns_false(self, repo):
        assert repo.delete(999, user_id="user_1") is False

    def test_delete_invalid_id_returns_false(self, repo):
        assert repo.delete("bad", user_id="user_1") is False


# ---------------------------------------------------------------------------
# 6. Assessment data snapshot
# ---------------------------------------------------------------------------

class TestAssessmentSnapshot:
    def test_symptoms_are_stored(self, repo, sample_data):
        result = repo.create(sample_data)
        assert result["symptoms"] == sample_data["symptoms"]

    def test_diagnosis_result_is_stored(self, repo, sample_data):
        result = repo.create(sample_data)
        assert result["diagnosis_result"] == sample_data["diagnosis_result"]

    def test_image_ids_are_stored(self, repo, sample_data):
        result = repo.create(sample_data)
        assert result["image_ids"] == ["img_001"]

    def test_status_is_stored(self, repo, sample_data):
        result = repo.create(sample_data)
        assert result["status"] == "completed"

    def test_red_flag_fields_are_stored(self, repo, sample_data):
        data = {**sample_data, "is_red_flag": True, "red_flag_reasons": ["gasping"]}
        result = repo.create(data)
        assert result["is_red_flag"] is True
        assert result["red_flag_reasons"] == ["gasping"]


# ---------------------------------------------------------------------------
# 6b. Animal snapshot
# ---------------------------------------------------------------------------

class TestAnimalSnapshot:
    def test_animal_snapshot_is_stored(self, repo, sample_data):
        result = repo.create(sample_data)
        assert "animal" in result
        assert result["animal"] is not None

    def test_animal_snapshot_contains_all_fields(self, repo, sample_data):
        result = repo.create(sample_data)
        animal = result["animal"]
        expected_keys = {
            "id", "name", "animal_type", "breed", "gender",
            "age", "weight", "color", "health_status",
        }
        assert set(animal.keys()) == expected_keys

    def test_animal_snapshot_values_match_input(self, repo, sample_data):
        result = repo.create(sample_data)
        animal = result["animal"]
        assert animal["id"] == "animal_42"
        assert animal["name"] == "Moti"
        assert animal["animal_type"] == "Cow"
        assert animal["breed"] == "Sahiwal"
        assert animal["gender"] == "Female"
        assert animal["age"] == 5
        assert animal["weight"] == 350.0
        assert animal["color"] == "Brown"
        assert animal["health_status"] == "healthy"

    def test_animal_snapshot_none_when_not_provided(self, repo, sample_data):
        del sample_data["animal"]
        result = repo.create(sample_data)
        assert result.get("animal") is None

    def test_animal_snapshot_retrieved_by_get_by_id(self, repo, sample_data):
        created = repo.create(sample_data)
        fetched = repo.get_by_id(created["id"], user_id="user_1")
        assert fetched["animal"] == sample_data["animal"]

    def test_animal_snapshot_retrieved_by_assessment_id(self, repo, sample_data):
        repo.create(sample_data)
        fetched = repo.get_by_assessment_id("assessment_7", user_id="user_1")
        assert fetched["animal"] == sample_data["animal"]

    def test_animal_snapshot_retrieved_by_user_id(self, repo, sample_data):
        repo.create(sample_data)
        results = repo.get_by_user_id("user_1")
        assert len(results) == 1
        assert results[0]["animal"] == sample_data["animal"]


# ---------------------------------------------------------------------------
# 7. App factory wiring
# ---------------------------------------------------------------------------

class TestAppFactoryWiring:
    def test_vet_summary_repo_available_on_app(self):
        app = create_app("testing")
        assert hasattr(app, "vet_summary_repo")
        assert isinstance(
            app.vet_summary_repo,
            InMemoryVetCaseSummaryRepository,
        )
