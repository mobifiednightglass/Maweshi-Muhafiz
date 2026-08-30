"""
ImageStorageService — GridFS-backed storage for health-assessment photos.

Uses the same MongoDB connection already configured (MONGODB_URI /
MONGODB_DB_NAME) and stores files in a dedicated GridFS bucket
(``assessment_images``).  Each stored file's ObjectId is exposed as a
plain string ``file_id`` to remain consistent with the rest of the API.

Usage:
    service = ImageStorageService(uri, db_name)
    file_id  = service.save_image(file_stream, "wound.jpg", "image/jpeg")
    stream, content_type = service.get_image(file_id)
    deleted  = service.delete_image(file_id)
"""

import logging
from typing import Optional

import gridfs
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import MongoClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constraints
# ---------------------------------------------------------------------------

ALLOWED_CONTENT_TYPES = frozenset({
    "image/jpeg",
    "image/png",
    "image/webp",
})

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

_GRIDFS_BUCKET = "assessment_images"


# ---------------------------------------------------------------------------
# Custom exceptions — routes catch these and map to HTTP status codes
# ---------------------------------------------------------------------------

class ImageValidationError(Exception):
    """Raised when an image fails content-type or size validation."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


class ImageNotFoundError(Exception):
    """Raised when a requested image id does not exist."""

    def __init__(self, file_id: str):
        self.file_id = file_id
        super().__init__(f"Image with id {file_id} not found.")


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ImageStorageService:
    """GridFS-backed image storage for health-assessment photos."""

    def __init__(self, uri: str, db_name: str):
        self._client = MongoClient(uri)
        self._db = self._client[db_name]
        self._fs = gridfs.GridFS(self._db, collection=_GRIDFS_BUCKET)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_object_id(value) -> Optional[ObjectId]:
        """Safely coerce a value to ObjectId.  Returns None on failure."""
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(str(value))
        except (InvalidId, TypeError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_image(
        self,
        file_stream,
        filename: str,
        content_type: str,
    ) -> str:
        """Validate and persist an image, returning its string file_id.

        Parameters
        ----------
        file_stream : readable binary stream
            The incoming file data (e.g. Flask ``FileStorage.stream``).
        filename : str
            Original filename to store alongside the binary data.
        content_type : str
            MIME type of the image (must be one of the allowed types).

        Returns
        -------
        str
            The GridFS file id as a plain string.

        Raises
        ------
        ImageValidationError
            If *content_type* is not allowed or the file exceeds the
            maximum size limit.
        """
        errors: list[str] = []

        # -- Content-type check -------------------------------------------
        if content_type not in ALLOWED_CONTENT_TYPES:
            errors.append(
                f"Content type '{content_type}' is not allowed. "
                f"Accepted types: {', '.join(sorted(ALLOWED_CONTENT_TYPES))}."
            )

        # -- Read data upfront to enforce size limit before storing -------
        data = file_stream.read()

        if len(data) > MAX_FILE_SIZE_BYTES:
            errors.append(
                f"File size ({len(data)} bytes) exceeds the maximum "
                f"allowed size of {MAX_FILE_SIZE_BYTES} bytes (5 MB)."
            )

        if errors:
            raise ImageValidationError(errors)

        # -- Store in GridFS ----------------------------------------------
        file_id = self._fs.put(
            data,
            filename=filename,
            content_type=content_type,
        )
        return str(file_id)

    def get_image(self, file_id: str) -> Optional[tuple]:
        """Retrieve an image by its string file_id.

        Returns
        -------
        tuple[bytes, str] or None
            ``(file_data, content_type)`` if found, ``None`` otherwise.
            Malformed ids return ``None`` silently.
        """
        oid = self._to_object_id(file_id)
        if oid is None:
            return None

        try:
            if not self._fs.exists(oid):
                return None
            grid_out = self._fs.get(oid)
            return grid_out.read(), grid_out.content_type
        except gridfs.NoFile:
            return None
        except Exception:
            logger.exception("Unexpected error retrieving image %s", file_id)
            return None

    def delete_image(self, file_id: str) -> bool:
        """Delete an image by its string file_id.

        Returns ``True`` if a file was removed, ``False`` if the id was
        invalid or the file did not exist.  Never raises for malformed ids.
        """
        oid = self._to_object_id(file_id)
        if oid is None:
            return False

        try:
            if not self._fs.exists(oid):
                return False
            self._fs.delete(oid)
            return True
        except Exception:
            logger.exception("Unexpected error deleting image %s", file_id)
            return False
