"""Defines the characteristics of an iOS version number."""

import attr

from .version import ShipItVersion


@attr.s(frozen=True, eq=False, hash=True)
class MobileIosVersion(ShipItVersion):
    """
    Class representing an iOS version number.

    iOS version numbers are a bit different in that they use the patch number as beta
    indicator instead since appstoreconnect doesn't allow us to ship versions with a `b`
    suffix in it.
    """

    def _create_bump_kwargs(self, field):
        """
        Create a version bump for the required field.

        Version bumping is a bit different for iOS as we use the patch number as a
        beta indicator.
        When asked to bump the patch version, bump the minor instead and remove any
        patch number.
        When asked to bump the beta number, bump the patch instead.
        """
        delete_zero_patch_number = True

        # IOS doesn't do patch numbers in versions, increment the minor number instead
        if field == "patch_number":
            field = "minor_number"

        # IOS doesn't do beta versions either. So instead we use the patch component
        # for that
        if field == "beta_number":
            field = "patch_number"
            delete_zero_patch_number = False

        kwargs = super()._create_bump_kwargs(field)
        if delete_zero_patch_number and kwargs.get("patch_number", 0) == 0:
            del kwargs["patch_number"]
        return kwargs

    @property
    def is_beta(self):
        """
        Returns true if the version is considered a beta one.

        For iOS versions, this is true when the version contains a patch number
        component.
        """
        return self.patch_number is not None

    @property
    def is_release_candidate(self):
        """
        Returns true if the version is a release candidate.

        For iOS versions, this is always false.
        """
        return False
