def toposort(data):
    """Topologically sort a graph

    :param data: A dictionary of sets, where the keys are vertices,
    and the values are the dependencies of each vertex

    :rtype: List

    Returns a list of vertices such that a vertex's dependencies always appear before
    the vertex itself.
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary of sets")

    # dont bother with empty data
    if len(data) == 0:
        return []

    #ignore self dependencies
    for k, v in data.items():
        if not isinstance(v, set):
            raise TypeError("All values must be sets")
        v.discard(k)

    #add any missing nodes with no dependencies
    extra_deps = reduce(set.union, data.values()) - set(data.keys())
    data.update({item:set() for item in extra_deps})

    result = []
    while True:
        #remove items with no remaining dependencies
        ordered = set(item for item, dep in data.items() if not dep)
        if not ordered:
            break
        result.extend(sorted(ordered))

        # mark dependencies as satisfied
        data = {item : (dep - ordered) for item, dep in data.items()
                if item not in ordered}
    if data:
        raise TypeError("A cyclic dependency exists amongst %r" % data)

    return result
