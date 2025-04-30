import ctypes
import numpy as np
import os
from pathlib import Path
from numba import njit
from lib.tama.rules import get_possible_moves as get_possible_moves2

dir_path = os.path.dirname(os.path.realpath(__file__))
lib = ctypes.CDLL(dir_path / Path('../../../libc/cmake-build-debug/libc.so'))
MOVES_POINTER = np.ctypeslib.ndpointer(dtype=np.intc, ndim=2, flags='C_CONTIGUOUS')
FIELD_POINTER = np.ctypeslib.ndpointer(dtype=np.intc, ndim=2, flags='C_CONTIGUOUS')

get_possible_moves_c = lib.get_possible_moves
get_possible_moves_c.argtypes = [MOVES_POINTER, FIELD_POINTER, ctypes.c_int]
get_possible_moves_c.restype = None

make_move_without_capture = lib.make_move_without_capture
make_move_without_capture.argtypes = [
    FIELD_POINTER, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
]
make_move_without_capture.restype = None

make_move_with_capture = lib.make_move_with_capture
make_move_with_capture.argtypes = [
    FIELD_POINTER, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int
]
make_move_with_capture.restype = None


def get_possible_moves(field: np.ndarray, side: int):
    moves = np.zeros((10000, 5), dtype=np.intc)
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
    moves = get_possible_moves2(start_field, 1)
    print(moves[0: moves[0][0]])


if __name__ == '__main__':
    main()
