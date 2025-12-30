"""
Simple In-Memory Artifact Service

Implements a basic artifact storage service for development,
following the ADK Artifacts pattern.
"""

import logging
from typing import Dict, Optional
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


class InMemoryArtifactService:
    """
    Simple in-memory artifact storage service.

    Stores artifacts (files as genai_types.Part) in memory for the session.
    Suitable for development and testing.
    """

    def __init__(self):
        """Initialize the in-memory artifact store."""
        self._artifacts: Dict[str, genai_types.Part] = {}
        logger.info("Initialized InMemoryArtifactService")

    def save(self, filename: str, artifact: genai_types.Part, namespace: str = "session") -> None:
        """
        Save an artifact.

        Args:
            filename: Unique identifier for the artifact
            artifact: The artifact as a genai_types.Part
            namespace: Namespace for the artifact (default: "session")
        """
        key = f"{namespace}:{filename}"
        self._artifacts[key] = artifact
        logger.info(f"Saved artifact: {key} ({len(artifact.inline_data.data)} bytes)")

    def load(self, filename: str, namespace: str = "session") -> Optional[genai_types.Part]:
        """
        Load an artifact.

        Args:
            filename: Unique identifier for the artifact
            namespace: Namespace for the artifact (default: "session")

        Returns:
            The artifact as a genai_types.Part, or None if not found
        """
        key = f"{namespace}:{filename}"
        artifact = self._artifacts.get(key)
        if artifact:
            logger.info(f"Loaded artifact: {key}")
        else:
            logger.warning(f"Artifact not found: {key}")
        return artifact

    def delete(self, filename: str, namespace: str = "session") -> bool:
        """
        Delete an artifact.

        Args:
            filename: Unique identifier for the artifact
            namespace: Namespace for the artifact (default: "session")

        Returns:
            True if deleted, False if not found
        """
        key = f"{namespace}:{filename}"
        if key in self._artifacts:
            del self._artifacts[key]
            logger.info(f"Deleted artifact: {key}")
            return True
        logger.warning(f"Artifact not found for deletion: {key}")
        return False

    def list(self, namespace: str = "session") -> list[str]:
        """
        List all artifacts in a namespace.

        Args:
            namespace: Namespace to list (default: "session")

        Returns:
            List of artifact filenames
        """
        prefix = f"{namespace}:"
        return [key.replace(prefix, "") for key in self._artifacts.keys() if key.startswith(prefix)]

    def clear(self, namespace: Optional[str] = None) -> None:
        """
        Clear all artifacts, optionally filtered by namespace.

        Args:
            namespace: If provided, only clear artifacts in this namespace
        """
        if namespace:
            keys_to_delete = [
                key for key in self._artifacts.keys() if key.startswith(f"{namespace}:")
            ]
            for key in keys_to_delete:
                del self._artifacts[key]
            logger.info(f"Cleared {len(keys_to_delete)} artifacts from namespace: {namespace}")
        else:
            count = len(self._artifacts)
            self._artifacts.clear()
            logger.info(f"Cleared all {count} artifacts")

    def __len__(self) -> int:
        """Return the number of stored artifacts."""
        return len(self._artifacts)
