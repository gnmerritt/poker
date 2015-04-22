from libc.stdlib cimport rand
cdef extern from "limits.h":
    int RAND_MAX


cpdef float uniform(float lower, float upper):
    """Cython wrapper around Python's random.uniform"""
    cdef float multiplier = (float)(rand() / RAND_MAX)
    cdef float range = upper - lower
    return lower + (range * multiplier)

cpdef int randint(int lower, int upper):
    cdef int range = upper - lower
    # special case to avoid % 1 (always 0)
    if range == 1:
        range = 2
    return lower + (rand() % range)

cpdef list sample(list population, int num_wanted):
    """Random sampling without replacement"""
    cdef int population_len = len(population)
    cdef uniform_len = population_len - 1
    if num_wanted >= population_len or uniform_len == 0:
        return population

    cdef dict chosen = {}
    cdef list picks = []
    cdef int picked = 0
    cdef int index
    while picked < num_wanted:
        index = randint(0, population_len)
        if not chosen.get(index):
            chosen[index] = True
            picks.append(population[index])
            picked += 1

    return picks
