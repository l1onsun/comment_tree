def pytest_configure(config):
    config.addinivalue_line(
        "markers", "integration: mark test to run only in integration environment"
    )
    config.addinivalue_line(
        "markers", "provider_override: mark test to override dependencies"
    )


def pytest_collection_modifyitems(items, config):
    for item in items:
        if not any(item.iter_markers("integration")):
            item.add_marker("unit")
