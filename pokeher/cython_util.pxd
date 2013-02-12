# Rich compare helper once we've constructed a compare integer
cdef inline bint richcmp_helper(int compare, int op):
    """Returns True/False for each compare operation given an op code.
    Make sure compare does what you want it to"""
    if op == 2: # ==
        return compare == 0
    elif op == 3: # !=
        return compare != 0
    if op == 0: # <
        return compare < 0
    elif op == 1: # <=
        return compare <= 0
    elif op == 4: # >
        return compare > 0
    elif op == 5: # >=
        return compare >= 0
