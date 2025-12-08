"""Static analysis and metrics computation service.

This module provides functions to compute:
- lines of code
- cyclomatic complexity (via radon)
- maintainability index (via radon)
- pylint score (parsed from CLI output)
- dependency count (import statements)
- duplication percentage (simple token-based heuristic)
- estimated bug probability (formula based on metrics)
"""

from __future__ import annotations

import io
import re
import statistics
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict

from radon.complexity import cc_visit
from radon.metrics import mi_visit


def _compute_loc(source: str) -> int:
    return len([line for line in source.splitlines() if line.strip()])


def _compute_cyclomatic_complexity(source: str) -> float:
    blocks = cc_visit(source)
    if not blocks:
        return 0.0
    return float(statistics.mean(b.complexity for b in blocks))


def _compute_maintainability_index(source: str) -> float:
    # radon returns MI on a 0-100 scale by default
    return float(mi_visit(source, True))


def _run_pylint_on_source(source: str) -> float:
    """Run pylint on the given source string and return the global score.

    We write the code to a temporary file and call pylint on that file.
    If pylint is not available or fails, we return 0.0.
    """

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir) / "temp_module.py"
            tmp_path.write_text(source, encoding="utf-8")

            # Run pylint with a very quiet output format
            proc = subprocess.run(
                ["pylint", str(tmp_path), "--score=y", "-rn"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            match = re.search(r"Your code has been rated at ([0-9.]+)/10", proc.stdout)
            if not match:
                return 0.0
            return float(match.group(1))
    except FileNotFoundError:
        # pylint not installed in environment
        return 0.0
    except Exception:
        return 0.0


def _compute_dependency_count(source: str) -> int:
    pattern = re.compile(r"^(from\s+\S+\s+import\s+\S+|import\s+\S+)")
    return sum(1 for line in source.splitlines() if pattern.match(line.strip()))


def _compute_duplication_percentage(source: str) -> float:
    """Very simple duplication heuristic based on repeated non-empty lines."""

    lines = [ln.strip() for ln in source.splitlines() if ln.strip()]
    if not lines:
        return 0.0
    total = len(lines)
    unique = len(set(lines))
    duplicated = max(0, total - unique)
    return float(duplicated) / float(total) * 100.0


def _estimate_bug_probability(
    loc: int,
    avg_complexity: float,
    maintainability_index: float,
    pylint_score: float,
) -> float:
    """Estimate bug probability using a heuristic formula.

    Higher LOC and complexity increase risk, higher MI and pylint score reduce it.
    Output is clamped to [0, 1].
    """

    # Normalize components
    loc_factor = min(loc / 1000.0, 2.0)  # cap largish projects
    complexity_factor = min(avg_complexity / 10.0, 2.0)
    mi_factor = 1.0 - min(max(maintainability_index, 0.0), 100.0) / 100.0
    pylint_factor = 1.0 - min(max(pylint_score, 0.0), 10.0) / 10.0

    raw = 0.25 * loc_factor + 0.35 * complexity_factor + 0.2 * mi_factor + 0.2 * pylint_factor
    return max(0.0, min(raw / 2.0, 1.0))


def compute_code_metrics(source: str) -> Dict[str, Any]:
    """Compute a suite of static-analysis metrics for the given source code."""

    loc = _compute_loc(source)
    avg_complexity = _compute_cyclomatic_complexity(source)
    mi_score = _compute_maintainability_index(source)
    pylint_score = _run_pylint_on_source(source)
    dependency_count = _compute_dependency_count(source)
    duplication_pct = _compute_duplication_percentage(source)
    bug_prob = _estimate_bug_probability(loc, avg_complexity, mi_score, pylint_score)

    return {
        "loc": loc,
        "cyclomatic_complexity": avg_complexity,
        "maintainability_index": mi_score,
        "pylint_score": pylint_score,
        "dependency_count": dependency_count,
        "duplication_percentage": duplication_pct,
        "estimated_bug_probability": bug_prob,
    }


def compute_basic_metrics_placeholder() -> Dict[str, Any]:
    """Backward-compatible wrapper used by existing placeholder endpoints."""

    return {
        "loc": 0,
        "cyclomatic_complexity": 0.0,
        "maintainability_index": 0.0,
        "pylint_score": 0.0,
        "dependency_count": 0,
        "duplication_percentage": 0.0,
        "estimated_bug_probability": 0.0,
    }
