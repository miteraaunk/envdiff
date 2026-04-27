"""Compare two parsed .env dictionaries and report differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Holds the comparison result between two .env files."""

    left_label: str
    right_label: str
    missing_in_right: List[str] = field(default_factory=list)
    missing_in_left: List[str] = field(default_factory=list)
    value_mismatches: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_right or self.missing_in_left or self.value_mismatches
        )

    def summary(self) -> str:
        lines = []
        for key in sorted(self.missing_in_right):
            lines.append(f"  - {key!r} present in [{self.left_label}] but missing in [{self.right_label}]")
        for key in sorted(self.missing_in_left):
            lines.append(f"  - {key!r} present in [{self.right_label}] but missing in [{self.left_label}]")
        for key in sorted(self.value_mismatches):
            left_val, right_val = self.value_mismatches[key]
            lines.append(
                f"  ~ {key!r} differs: [{self.left_label}]={left_val!r} vs [{self.right_label}]={right_val!r}"
            )
        return "\n".join(lines) if lines else "No differences found."


def compare_envs(
    left: Dict[str, Optional[str]],
    right: Dict[str, Optional[str]],
    left_label: str = "left",
    right_label: str = "right",
) -> DiffResult:
    """Compare two env dicts and return a DiffResult."""
    result = DiffResult(left_label=left_label, right_label=right_label)

    left_keys = set(left.keys())
    right_keys = set(right.keys())

    result.missing_in_right = sorted(left_keys - right_keys)
    result.missing_in_left = sorted(right_keys - left_keys)

    for key in left_keys & right_keys:
        if left[key] != right[key]:
            result.value_mismatches[key] = (left[key], right[key])

    return result
