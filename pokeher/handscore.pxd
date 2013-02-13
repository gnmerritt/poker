cdef class HandScore:
    cdef public int type
    cdef public object kicker

cdef class HandBuilder:
    cdef object cards

    cpdef int select_flush_suit(self)
    cpdef bint is_straight(self)
