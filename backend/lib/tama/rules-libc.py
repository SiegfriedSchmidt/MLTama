import ctypes
import numpy as np
from numba import njit

lib = ctypes.CDLL('../../../libc/cmake-build-debug/libc.so')
MOVES_POINTER = np.ctypeslib.ndpointer(dtype=np.intc, ndim=2, flags='C_CONTIGUOUS')
FIELD_POINTER = np.ctypeslib.ndpointer(dtype=np.intc, ndim=2, flags='C_CONTIGUOUS')

get_possible_moves_c = lib.get_possible_moves
get_possible_moves_c.argtypes = [MOVES_POINTER, FIELD_POINTER, ctypes.c_int]
get_possible_moves_c.restype = None


def get_possible_moves(field: np.ndarray, side: int):
    moves = np.zeros((10000, 5), dtype=np.int32)
    get_possible_moves_c(moves, field, side)
    return moves


def main():
    start_field = np.array([
        [0, 0, 0, 0, 0, -1, 0, 0],
        [-1, -1, -1, -1, -1, 0, -1, -1],
        [-1, -1, -1, -1, 0, -1, -1, -1],
        [0, 0, -1, 0, -1, 0, 0, 0],
        [-1, -1, 0, 0, 0, -1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ], dtype=np.intc)

    moves = get_possible_moves(start_field, 1)
    print(moves[0: moves[0][0]])


if __name__ == '__main__':
    main()
