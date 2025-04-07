from numba import config

# config.DISABLE_JIT = True

import numpy as np
from time import time
from numba import njit
from lib.tama.rules import get_possible_moves, make_move_with_capture, make_move_without_capture
from lib.fen import fen_to_field
from lib.tama.helpers import field_to_fen_numba

pieces_eval_arrays = np.zeros((5, 8, 8), dtype=np.int32)

for i in range(8):
    for j in range(8):
        if i == 0 or i == 7:
            continue
        pieces_eval_arrays[1, i, j] = max(10, 10 + (6 - i) * 2)
        pieces_eval_arrays[-1, i, j] = min(-10, -10 - (i - 1) * 2)
        pieces_eval_arrays[2] = 100
        pieces_eval_arrays[-2] = -100


@njit()
def evaluate_node(field):
    value = 0
    white_count = 0
    black_count = 0
    for i in range(8):
        for j in range(8):
            if field[i, j] > 0:
                white_count += 1
            elif field[i, j] < 0:
                black_count += 1
            value += pieces_eval_arrays[field[i, j], i, j]

    if white_count == 0:
        return -10000
    elif black_count == 0:
        return 10000
    return value


@njit()
def evaluate_node_at_depth(stats, field_copy, side, depth):
    field = field_copy.copy()
    moves = get_possible_moves(field_copy, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    alpha = -999999
    beta = 999999
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture):
                make_move_with_capture(field, moves[j, 2], moves[j, 3], moves[j + 1, 0], moves[j + 1, 1],
                                       moves[j + 1, 2], moves[j + 1, 3], moves[j + 1, 4])

            value = -negamax(stats, field, depth - 1, -beta, -alpha, -side)
            alpha = max(alpha, value)
            field = field_copy.copy()

            yield i, value, i == moves_idx - max_capture - 1
    else:
        for i in range(1, moves_idx):
            make_move_without_capture(field, moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3], moves[i, 4])

            value = -negamax(stats, field, depth - 1, -beta, -alpha, -side)
            alpha = max(alpha, value)
            field = field_copy.copy()

            yield i, value, i == moves_idx - 1


@njit()
def negamax(stats, field_copy, depth, alpha, beta, side):
    if depth == 0:
        stats[0] += 1
        return evaluate_node(field_copy) * side

    moves = get_possible_moves(field_copy, side)
    moves_idx, max_capture = moves[0, 0], moves[0, 1]

    # is terminal node
    if moves_idx == 1:
        stats[0] += 1
        return -10000

    field = field_copy.copy()
    stats[1] = max(stats[1], moves_idx)

    value = -999999
    if max_capture:
        for i in range(1, moves_idx, max_capture + 1):
            for j in range(i, i + max_capture):
                make_move_with_capture(field, moves[j, 2], moves[j, 3], moves[j + 1, 0], moves[j + 1, 1],
                                       moves[j + 1, 2], moves[j + 1, 3], moves[j + 1, 4])

            next_depth = depth - 1 if depth > 1 else depth
            value = max(value, -negamax(stats, field, next_depth, -beta, -alpha, -side))
            alpha = max(alpha, value)
            if alpha >= beta:
                break

            field = field_copy.copy()
    else:
        for i in range(1, moves_idx):
            make_move_without_capture(field, moves[i, 0], moves[i, 1], moves[i, 2], moves[i, 3], moves[i, 4])

            value = max(value, -negamax(stats, field, depth - 1, -beta, -alpha, -side))
            alpha = max(alpha, value)
            if alpha >= beta:
                break

            field = field_copy.copy()

    return value


# compile
test_field = fen_to_field('8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w')
test_stats = np.array([0, 0], dtype=np.int64)
evaluate_node_at_depth(test_stats, test_field, 1, 2)


def main():
    from lib.tama.iterative_descent import iterative_descent
    field = fen_to_field('b4B2/2W5/8/3w1w2/8/8/w2w1w1w/1W2w1w1/ b')
    possible = get_possible_moves(field, -1)
    print(possible[0])

    field = fen_to_field('w1w1w1w1/1w1w1w1w/8/3b1b2/2w1w1w1/1b1b1b1b/b1b1b1b1/1b1b1b1b b')
    print(field)
    print('start')
    print(evaluate_node(field))
    t = time()
    iterative_descent(evaluate_node_at_depth, field, 1, 10)
    print(f"time: {time() - t:.2f}")


if __name__ == '__main__':
    main()
'''
'8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w'
moves = np.zeros((1500, 5), dtype=np.uint32)
1 [20925520     1081]
time: 36.09
1 [20925520     1081]
time: 35.61
1 [20925520     1081]
time: 35.12

moves = np.zeros((1500, 5), dtype=np.uint16)
1 [20925520     1081]
time: 33.53
1 [20925520     1081]
time: 35.94
1 [20925520     1081]
time: 33.06

moves = np.zeros((1100, 5), dtype=np.uint16)
1 [20925520     1081]
time: 33.14
1 [20925520     1081]
time: 34.30
1 [20925520     1081]
time: 34.53

moves = np.empty((1100, 5), dtype=np.uint16)
1 [20925520     1081]
time: 35.33
1 [20925520     1081]
time: 36.27
1 [20925520     1081]
time: 33.91

'8/wwwwwwww/wwwwwwww/8/8/bbbbbbbb/bbbbbbbb/8 w'
moves = np.empty((1100, 5), dtype=np.uint16)
1 [19344153       56]
time: 96.65
1 [19344153       56]
time: 93.64
1 [19344153       56]
time: 94.59
1 [19344153       56]
time: 97.76

moves = np.empty((1100, 5), dtype=np.uint8) 17,3 GB
1 [19344153       56]
time: 94.45

moves = np.empty((1100, 5), dtype=np.uint32)
1 [19344153       56]
time: 100.40
1 [19344153       56]
time: 98.53
1 [19344153       56]
time: 101.09

moves = np.empty((1100, 5), dtype=np.int32)
1 [19344153       56]
time: 95.93
1 [19344153       56]
time: 105.52

moves = np.empty((1100, 5), dtype=np.int64) 17,3 GB
1 [19344153       56]
time: 104.71
1 [19344153       56]
time: 104.52

moves = np.empty((60, 5), dtype=np.int64)
1 [19344153       56]
time: 95.33

moves = np.empty((60, 5), dtype=np.uint8)
1 [19344153       56]
time: 96.86

'8/wwwwwwww/wwwww1ww/8/2b1bWb1/b1bb2bb/bbbbb1b1/8/ w'
moves = np.empty((1500, 5), dtype=np.uint32
1 [20925520     1081]
time: 34.17

moves = np.empty((1500, 5), dtype=np.int32) 15,5 GB
1 [20925520     1081]
time: 33.70
1 [20925520     1081]
time: 36.66

WITH MOVE GENERATOR 14,8GB - 36,6GB = -21,8 GB
1 [29832695        0]
time: 36.87
1 [29832695        0]
time: 39.16


-----------------------------------
1 [38  0] 4.172325134277344e-05 [(1, -3), (2, -3), (3, -3), (4, -3), (5, -3), (6, -3), (7, -3), (8, -3), (9, -3), (10, -3), (11, -3), (12, -3), (13, -3), (14, -3), (15, -3), (16, -3), (17, -3), (18, -3), (19, -3), (20, -3), (21, -3), (22, -3), (23, -3), (24, -3), (25, -3), (26, -3), (27, -3), (28, -3), (29, -3), (30, -3), (31, -3), (32, -3), (33, -3), (34, -3), (35, -3), (36, -3), (37, -3), (38, -3)]
2 [120  46] 0.0003871917724609375 [(3, -3), (4, -3), (6, -3), (7, -3), (10, -3), (11, -3), (12, -3), (13, -3), (14, -3), (15, -3), (16, -3), (18, -3), (19, -3), (20, -3), (21, -3), (23, -3), (24, -3), (25, -3), (26, -3), (27, -3), (28, -3), (29, -3), (30, -3), (31, -3), (32, -3), (33, -3), (34, -3), (35, -3), (36, -3), (37, -3), (38, -3), (1, -4), (2, -4), (5, -4), (8, -4), (9, -4), (17, -4), (22, -4)]
3 [1582   46] 0.0017979145050048828 [(3, -3), (4, -3), (5, -3), (6, -3), (7, -3), (8, -3), (9, -3), (10, -3), (11, -3), (12, -3), (13, -3), (14, -3), (15, -3), (16, -3), (17, -3), (18, -3), (19, -3), (20, -3), (21, -3), (22, -3), (23, -3), (24, -3), (25, -3), (26, -3), (27, -3), (28, -3), (29, -3), (30, -3), (31, -3), (32, -3), (33, -3), (34, -3), (35, -3), (36, -3), (37, -3), (38, -3), (1, -4), (2, -4)]
4 [39516    51] 0.04971599578857422 [(1, -4), (2, -4), (3, -4), (4, -4), (5, -4), (6, -4), (7, -4), (8, -4), (9, -4), (10, -4), (11, -4), (12, -4), (13, -4), (14, -4), (15, -4), (16, -4), (17, -4), (18, -4), (19, -4), (20, -4), (21, -4), (22, -4), (23, -4), (24, -4), (25, -4), (26, -4), (27, -4), (28, -4), (29, -4), (30, -4), (31, -4), (32, -4), (33, -4), (34, -4), (35, -4), (36, -4), (37, -4), (38, -4)]
5 [118779   1863] 0.22851157188415527 [(10, -3), (11, -3), (12, -3), (13, -3), (14, -3), (15, -3), (16, -3), (17, -3), (18, -3), (19, -3), (20, -3), (21, -3), (22, -3), (23, -3), (24, -3), (25, -3), (26, -3), (27, -3), (28, -3), (29, -3), (30, -3), (31, -3), (32, -3), (33, -3), (34, -3), (35, -3), (36, -3), (37, -3), (38, -3), (1, -4), (2, -4), (3, -4), (4, -4), (5, -4), (6, -4), (7, -4), (8, -4), (9, -4)]
6 [1943120    1863] 2.670663595199585 [(34, -3), (35, -3), (36, -3), (37, -3), (38, -3), (10, -4), (11, -4), (12, -4), (13, -4), (14, -4), (15, -4), (16, -4), (17, -4), (18, -4), (19, -4), (20, -4), (21, -4), (22, -4), (23, -4), (24, -4), (25, -4), (26, -4), (27, -4), (28, -4), (29, -4), (30, -4), (31, -4), (32, -4), (33, -4), (1, -5), (2, -5), (3, -5), (4, -5), (5, -5), (6, -5), (7, -5), (8, -5), (9, -5)]
7 [6041648    2339] 10.728743314743042 [(10, -3), (11, -3), (12, -3), (13, -3), (14, -3), (15, -3), (16, -3), (17, -3), (18, -3), (19, -3), (20, -3), (21, -3), (22, -3), (23, -3), (24, -3), (25, -3), (26, -3), (27, -3), (28, -3), (29, -3), (30, -3), (31, -3), (32, -3), (33, -3), (34, -3), (35, -3), (36, -3), (37, -3), (38, -3), (1, -4), (2, -4), (3, -4), (4, -4), (5, -4), (6, -4), (7, -4), (8, -4), (9, -4)]

[13 16 14 15 11 12 10 25 24 23 22 21 20 19 18 17 29 26 27 28 31 30 32 33
 36 35 38 37 34  2  9  1  5  8  3  4  7  6]
[-3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3 -3
 -3 -3 -3 -3 -3 -4 -4 -4 -4 -4 -9 -9 -9 -9]

'''
