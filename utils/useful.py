def batch(container: iter, n: int):
    for i in range(0, len(container), n):
        yield container[i:i + n]


def batch2(container: iter, n: int):
    for i in range(0, len(container)):
        step = min(i + n, len(container))
        yield container[i:step]
