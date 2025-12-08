from dataclasses import dataclass
from typing import List


@dataclass
class FeatureVector:
    prompt_length: int
    word_count: int
    feature_count: int
    num_technologies: int
    has_react: int
    has_fastapi: int

    def to_list(self) -> List[float]:
        return [
            float(self.prompt_length),
            float(self.word_count),
            float(self.feature_count),
            float(self.num_technologies),
            float(self.has_react),
            float(self.has_fastapi),
        ]


class FeatureExtractor:
    """Extracts simple numeric features from idea, features, and stack text.

    Feature vector:
        [prompt_length, word_count, feature_count, num_technologies, has_react, has_fastapi]
    """

    def _extract_prompt_features(self, idea: str) -> tuple[int, int]:
        idea = idea or ""
        prompt_length = len(idea)
        word_count = len(idea.split()) if idea.strip() else 0
        return prompt_length, word_count

    def _extract_feature_count(self, features: str) -> int:
        features = features or ""
        if not features.strip():
            return 0
        # Count commas + 1, e.g. "a, b, c" -> 3
        return features.count(",") + 1

    def _extract_stack_features(self, stack: str) -> tuple[int, int, int]:
        stack = stack or ""
        tokens = [t for t in stack.split() if t]
        num_technologies = len(tokens)
        has_react = 1 if any(t.lower() == "react" for t in tokens) else 0
        has_fastapi = 1 if any(t.lower() == "fastapi" for t in tokens) else 0
        return num_technologies, has_react, has_fastapi

    def transform(self, idea: str, features: str, stack: str) -> FeatureVector:
        prompt_length, word_count = self._extract_prompt_features(idea)
        feature_count = self._extract_feature_count(features)
        num_technologies, has_react, has_fastapi = self._extract_stack_features(stack)

        return FeatureVector(
            prompt_length=prompt_length,
            word_count=word_count,
            feature_count=feature_count,
            num_technologies=num_technologies,
            has_react=has_react,
            has_fastapi=has_fastapi,
        )

    def transform_to_list(self, idea: str, features: str, stack: str) -> List[float]:
        return self.transform(idea, features, stack).to_list()
