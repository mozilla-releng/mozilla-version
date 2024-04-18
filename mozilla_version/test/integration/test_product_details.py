from mozilla_version.test.integration import skip_network_tests_by_default


@skip_network_tests_by_default
def test_dummy_skipped_test():
    assert True
