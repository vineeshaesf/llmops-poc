def retrieve_context(query):
    with open("docs/common_errors.txt") as f:
        data = f.read()

    if "package" in query.lower():
        return data

    return data[:500]
