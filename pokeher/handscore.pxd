cdef class HandScore:
    cdef public int type
    cdef public object kicker

cdef class HandBuilder:
    cdef list cards

    cpdef int select_flush_suit(self)
    cpdef bint is_straight(self)
    cpdef list __score_cards_to_ranks(self, HandScore score)
