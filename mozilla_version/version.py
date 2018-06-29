"""Defines common characteristics of a version at Mozilla."""

from enum import Enum


class VersionType(Enum):
    """Enum that sorts types of versions (e.g.: nightly, beta, release, esr).

    Supports comparison.
    """

    NIGHTLY = 1
    AURORA_OR_DEVEDITION = 2
    BETA = 3
    RELEASE = 4
    # ESR has the same value than RELEASE because 60.0.1 is the same codebase
    # than 60.0.1esr, for instance
    ESR = 4

    def __eq__(self, other):
        """Implement `==` operator.

        `RELEASE` and `ESR` are considered equal because 60.0.1 is the same codebase
        than 60.0.1esr, for instance

        Example:
            `assert VersionType.NIGHTLY == VersionType.NIGHTLY`
            `assert VersionType.ESR == VersionType.RELEASE`
        """
        return self.compare(other) == 0

    def __ne__(self, other):
        """Implement `!=` operator."""
        return self.compare(other) != 0

    def __lt__(self, other):
        """Implement `<` operator."""
        return self.compare(other) < 0

    def __le__(self, other):
        """Implement `<=` operator."""
        return self.compare(other) <= 0

    def __gt__(self, other):
        """Implement `>` operator."""
        return self.compare(other) > 0

    def __ge__(self, other):
        """Implement `>=` operator."""
        return self.compare(other) >= 0

    def compare(self, other):
        """Compare this `VersionType` with anotherself.

        Returns:
            0 if equal
            < 0 is this precedes the other
            > 0 if the other precedes this

        """
        return self.value - other.value
