import os
from distutils.util import strtobool

import pytest


def skip_network_tests_by_default(function):
    return pytest.mark.skipif(
        strtobool(os.environ.get("SKIP_NETWORK_TESTS", "true")),
        reason="Tests requiring network are skipped by default. Enable them by setting SKIP_NETWORK_TESTS=false",
    )(function)
