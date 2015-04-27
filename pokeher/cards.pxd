cdef class Card:
    cdef readonly int value, suit

cdef class Hand:
    cdef readonly Card high, low
    cpdef simple(self)
    cpdef bint is_pair(self)
    cpdef bint is_suited(self)
    cpdef int card_gap(self)
    cpdef bint is_connected(self)
