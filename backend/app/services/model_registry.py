"""Placeholder model registry service."""

from typing import Dict


class ModelRegistry:
    """Very small stub model registry.

    Will later support GPT-3.5, GPT-4, local HF and stub models.
    """

    def __init__(self) -> None:
        self.available_models = ["stub"]

    def get_default_model(self) -> str:
        """Return the default model identifier."""

        return "stub"


def get_model_registry() -> ModelRegistry:
    """Dependency-style accessor for the model registry."""

    return ModelRegistry()
