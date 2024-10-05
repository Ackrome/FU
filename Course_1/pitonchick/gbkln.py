def is_equal(lst, pattern):
    if len(lst) != len(pattern):
        return False
    for a, b in zip(lst, pattern):
        if a != b:
            return False
    return True

def clear2(lst, pattern):
    res = []
    l = len(pattern)
    r = iter(range(len(lst)))
    while True:
        try:
            i = next(r)
            if is_equal(lst[i:i+l], pattern):
                for j in range(i, i + l - 1):
                    next(r)
            else:
                res.append(lst[i])
        except StopIteration:
            break
    return res
l = [1, 2, 1, 2, 1, 1, 2, 1, 3, 4, 1, 2]
p = (1, 2, 1)
print(l)
print(clear2(l, p))