def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker in item.iter_markers():
            item.user_properties.append(("name", marker.name))
            item.user_properties.append(("args", marker.args))
            item.user_properties.append(("kwargs", marker.kwargs))
