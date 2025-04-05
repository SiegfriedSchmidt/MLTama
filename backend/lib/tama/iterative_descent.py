from time import time
from typing import Iterator, Callable

import numpy as np

from lib.tama.rules import get_possible_moves


def arrange_moves(unsorted_moves, moves_indexes: np.ndarray):
    # exploring better moves first
    max_capture = unsorted_moves[0, 1]
    moves = np.empty_like(unsorted_moves)
    moves[0] = unsorted_moves[0]

    new_move_idx = 1
    for move_idx in moves_indexes:
        if max_capture:
            moves[new_move_idx:new_move_idx + max_capture + 1] = unsorted_moves[move_idx:move_idx + max_capture + 1]
            new_move_idx += max_capture + 1
        else:
            moves[new_move_idx] = unsorted_moves[move_idx]
            new_move_idx += 1

    return moves


def get_indexes(moves):
    moves_idx, max_capture = moves[0, 0], moves[0, 1]
    if max_capture:
        return np.array([i for i in range(1, moves_idx, max_capture + 1)])
    else:
        return np.array([i for i in range(1, moves_idx)])


def iterative_descent(
        evaluate_node_at_depth: Callable[[np.ndarray, np.ndarray, np.ndarray, int, int], Iterator[int]],
        field: np.ndarray, side: int, think_time: int
):
    t = time()
    stats = np.array([0, 0], dtype=np.int64)
    moves = get_possible_moves(field, side)

    moves_indexes = get_indexes(moves)
    moves_values = np.zeros_like(moves_indexes)
    for depth in range(5, think_time):
        print('Depth: ', depth)
        for j in range(2):
            for i, evaluated in enumerate(evaluate_node_at_depth(stats, moves, field, side, depth)):
                print('.', end='')
                moves_values[i] = evaluated

            sorted_indexes = np.argsort(-moves_values)
            moves = arrange_moves(moves, get_indexes(moves)[sorted_indexes])

            moves_indexes = get_indexes(moves)[sorted_indexes]
            moves_values = moves_values[sorted_indexes]
            print()
            print(moves_indexes)
            print(moves_values)
            print(depth, stats, time() - t, moves_indexes[0], moves_values[0])

    # print(moves_indexes)
    # print(moves_values)
    return moves_indexes[moves_values == np.max(moves_values)][0]


'''
Depth:  5
......................................
 5 [182968   1863] 0.710493803024292 13 -3
Depth:  6
......................................
 6 [3156436    1863] 4.344146966934204 34 -3
Depth:  7
......................................
 7 [14920950     6189] 41.57973623275757 13 -3
[13 16 14 15 11 12 10 29 25 26 23 24 21 20 19 18 31 30 27 28 32 35 34 33
 36 37 38  2  9  1  8  5 17 22  7  6  3  4]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -5 -5 -9 -9]
time: 41.58

[34 13 14 16 11 12 10 15 24 23 21 20 18 19 29 25 33 36 27 26 31 30 32 28
 37 35 38 22 17  2  9  1  5  8  6  7  4  3]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -4 -4 -4 -4 -4 -4 -4 -5 -5 -9 -9]
time: 40.39
'''
